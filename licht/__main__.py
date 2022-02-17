"""
licht.__main__

@author: phdenzel
"""
import json
import licht
from licht.rest import LichtClient
from licht.app import LichtApplet


def main(verbose=False):
    bridge_ip = licht.bridge_ip
    licht_client = LichtClient(bridge_ip)
    if licht.args.register:
        licht_client.register_user(verbose=True)
    if licht.args.app_mode or licht.args.as_daemon:
        licht_applet = LichtApplet(client=licht_client)
        licht_applet.run()
    elif licht.args.list_lights:
        data = licht_client.fetch_lights()
        print("Lights")
        for idx, name in data.names.items():
            print(f"{idx:>3} :  {name}")
    elif licht.args.list_groups:
        data = licht_client.fetch_groups()
        print("Groups")
        for idx, name in data.names.items():
            print(f"{idx:>3} :  {name}")
    elif licht.args.list_scenes:
        data = licht_client.fetch_scenes()
        print("Scenes")
        for idx, name in data.names.items():
            print(f"{idx:>17} :  {name}")
    else:
        try:
            update = {}
            if licht.args.light:
                subpath = f'lights/{licht.args.light}'
            elif licht.args.group:
                subpath = f'groups/{licht.args.group}'
            elif licht.args.scene:
                data = licht_client.fetch_data().scenes.subset([licht.args.scene])
                subpath = data.put_path
                update["scene"] = licht.args.scene
            if licht.args.on is not None:
                update["on"] = licht.args.on
            if licht.args.bri is not None:
                update["bri"] = licht.args.bri
            if licht.args.ct is not None:
                update["ct"] = licht.args.ct
            if licht.args.update:
                update = json.loads(licht.args.update)
            licht_client.change_state(subpath=subpath, update=update)
        except Exception:
            licht.parser.print_help()


if __name__ == "__main__":
    main()
