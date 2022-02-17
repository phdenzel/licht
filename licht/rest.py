"""
licht.rest

@author: phdenzel
"""
import os
import requests
import logging
from pprint import pprint
from urllib.parse import urljoin
import licht


class LichtClientResponseError(requests.exceptions.RequestException):
    pass


class ProtoRESTClient(object):
    """ Basic REST client wrapper for general APIs """
    def __init__(self, uri, scheme='http'):
        self.session = requests.Session()
        self.scheme = scheme
        self.uri = uri
        self.rcache = []

    @property
    def url_base(self) -> str:
        return f'{self.scheme}://{self.uri}'

    def urlpath(self, *path_components) -> str:
        return "/".join(path_components)

    def get(self, url=None, subpath=None, verbose=False) -> requests.Response:
        if url is None:
            url = self.url_base
        if subpath is not None:
            url = self.urlpath(url, subpath)
        response = self.session.get(url)
        self.rcache.append(response)
        if verbose:
            try:
                content = response.json()
            except requests.exceptions.JSONDecodeError:
                content = response.text
            print(url)
            pprint(content)
        return response

    def put(self, url=None, subpath=None, data=None, verbose=False
            ) -> requests.Response:
        if url is None:
            url = self.url_base
        if subpath is not None:
            url = self.urlpath(url, subpath)
        response = self.session.put(url, json=data)
        self.rcache.append(response)
        if verbose:
            try:
                content = response.json()
            except requests.exceptions.JSONDecodeError:
                content = response.text
            print(url)
            pprint(content)
        return response

    def post(self, url=None, subpath=None, data=None, verbose=False
             ) -> requests.Response:
        if url is None:
            url = self.url_base
        if subpath is not None:
            url = self.urlpath(url, subpath)
        response = self.session.post(url, json=data)
        self.rcache.append(response)
        if verbose:
            try:
                content = response.json()
            except requests.exceptions.JSONDecodeError:
                content = response.text
            print(url)
            pprint(content)
        return response

    def delete(self, url=None, subpath=None, verbose=False
               ) -> requests.Response:
        if url is None:
            url = self.url_base
        if subpath is not None:
            url = self.urlpath(url, subpath)
        response = self.session.delete(url)
        self.rcache.append(response)
        if verbose:
            try:
                content = response.json()
            except requests.exceptions.JSONDecodeError:
                content = response.text
            print(url)
            pprint(content)
        return response

    @property
    def error_status(self) -> bool:
        return self.rcache[-1].status_code >= 400


class LichtClient(ProtoRESTClient):
    """ REST client for Philips Hue API system """

    no_username_message = (
        "Authentification required: no authorized username given!\n"
        "Please set an already registered username or \npress the "
        "button on the Philips Hue bridge and use "
        "<register_user()>.\nIt will automatically update the "
        "username in your configuration file.")

    def __init__(self, uri, scheme='http', api_subpath='api',
                 devicetype=None, username=None):
        super(LichtClient, self).__init__(uri, scheme=scheme)
        self.api_subpath = api_subpath
        self.devicetype = devicetype
        self.username = username
        if username is None and licht.username:
            self.username = licht.username
        if devicetype is None:
            self.devicetype = f'licht#{os.uname()[1]}'
        if self.username is None:
            print(self.no_username_message)

    @property
    def url_api(self) -> str:
        return urljoin(self.url_base, self.api_subpath)

    @property
    def url_user(self) -> str:
        return self.urlpath(self.url_api, self.username)

    def register_user(self, verbose=False) -> dict:
        url = self.url_api
        body = {"devicetype": self.devicetype}
        response = self.post(url=url, data=body)
        content = response.json()
        errors = ["error" in c for c in content]
        if self.error_status:
            raise response.raise_for_status(
                "Error during registration! Try again...")
        if sum(errors) == len(errors):
            err_descr = content[errors.index(True)]['error']['description']
            raise LichtClientResponseError(err_descr)
        elif sum(errors) > 0:
            err_descr = content[errors.index(True)]['error']['description']
            logging.error(f'Warning: {err_descr}')
        registration = None
        username = None
        for index in [i for i, err in enumerate(errors) if not err]:
            resp_success = content[index]['success']
            if 'username' in resp_success:
                registration = resp_success
        if registration:
            self.username = registration['username']
            licht.username = username
            licht.configs[licht.config_section].update(registration)
            licht.parsing.write_configs()
        if verbose:
            logging.info(f'Authentification response: {content}')
            logging.info(f'Username: {username}')
        return content

    def unregister_user(self, verbose=False) -> dict:
        if 'username' in licht.configs[licht.config_section]:
            del licht.configs[licht.config_section]['username']
        d = licht.parsing.write_configs()
        if verbose:
            print(d)
        url = self.urlpath(self.url_user, f'config/whitelist/{self.username}')
        response = self.delete(url, verbose=verbose)
        return response.json()

    def fetch_lights(self, verbose=False) -> licht.data.LichtLightsData:
        response = self.get(self.url_user, subpath='lights', verbose=verbose)
        return licht.data.LichtLightsData(response.json())

    def fetch_groups(self, verbose=False) -> licht.data.LichtGroupsData:
        response = self.get(self.url_user, subpath='groups', verbose=verbose)
        return licht.data.LichtGroupsData(response.json())

    def fetch_scenes(self, verbose=False) -> licht.data.LichtScenesData:
        """
        Fetch data of scenes
        """
        response = self.get(self.url_user, subpath='scenes', verbose=verbose)
        return licht.data.LichtScenesData(response.json())

    def fetch_data(self, verbose=False) -> licht.data.LichtFetchData:
        """
        Fetch data of all elements
        """
        ld = self.fetch_lights()
        gd = self.fetch_groups()
        sd = self.fetch_scenes()
        return licht.data.LichtFetchData(ld, gd, sd)

    def change_state(self, data=None, subpath=None, update={}):
        if data is None:
            data = self.fetch_data()
        if subpath is not None:
            data = data.from_path(subpath)
        subpath = data.put_path
        url = self.urlpath(self.url_user, subpath)
        states = [data[k][data.state_cmd] for k in data]
        if update:
            responses = []
            for state in states:
                response = self.put(url=url, data=update)
                responses.append(response)
        return responses

    def close(self):
        self.session.close()

    def __exit__(self):
        self.close()


def main():
    rc = LichtClient(licht.bridge_ip)
    rc.get(rc.url_user, verbose=True)


if __name__ == "__main__":
    main()
