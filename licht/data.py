"""
licht.data

@author: phdenzel
"""
from dataclasses import dataclass


@dataclass
class LichtProtoData:
    fetch_data: dict = None
    _path: str = ''
    state_cmd: str = ''

    def __getitem__(self, item):
        if item in self.fetch_data:
            return self.fetch_data[item]

    def __iter__(self):
        if self.fetch_data:
            return self.fetch_data.__iter__()
        return iter([])

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def put_path(self):
        return "/".join([self.path, self.state_cmd])

    @property
    def index(self) -> list:
        return list(self.fetch_data.keys())

    @property
    def names(self) -> dict:
        return {i: self[i]['name'] for i in self if 'name' in self[i]}

    @property
    def names_list(self) -> list:
        return list(self.names.values())

    def subset(self, set_list):
        obj = self.__class__({i: self[i] for i in set_list})
        if len(set_list) == 1:
            if isinstance(set_list, list):
                obj.path = "/".join([obj.path]+set_list)
            elif isinstance(set_list, str):
                obj.path += "/"+set_list
        return obj


@dataclass
class LichtLightsData(LichtProtoData):
    _path: str = 'lights'
    state_cmd: str = 'state'


@dataclass
class LichtGroupsData(LichtProtoData):
    _path: str = 'groups'
    state_cmd: str = 'action'

    @property
    def lights_index(self):
        return {i: self[i]['lights'] for i in self if 'lights' in self[i]}

    def with_lights(self, *lights_ids):
        group_ids = [i for i, li in self.lights_index.items()
                     if all(lij in li for lij in lights_ids)]
        return self.subset(group_ids)


@dataclass
class LichtScenesData(LichtProtoData):
    _path: str = 'scenes'
    state_cmd: str = 'action'

    @property
    def group_index(self):
        return {i: self[i]['group'] for i in self if 'group' in self[i]}

    def in_groups(self, *groups_ids):
        scene_ids = [i for i, gi in self.group_index.items() if gi in groups_ids]
        return self.subset(scene_ids)

    @property
    def lights_index(self):
        return {i: self[i]['lights'] for i in self if 'lights' in self[i]}

    def with_lights(self, *lights_ids):
        scene_ids = [i for i, li in self.lights_index.items()
                     if all(lij in li for lij in lights_ids)]
        return self.subset(scene_ids)

    @property
    def path(self):
        gi = self.group_index
        if len(gi) == 1:
            return f"groups/{gi[list(gi.keys())[0]]}"
        return self._path

    @path.setter
    def path(self, path):
        self._path = path


@dataclass
class LichtFetchData:
    lights: LichtLightsData
    groups: LichtGroupsData
    scenes: LichtScenesData

    @classmethod
    def from_fetch(cls, lights_data, groups_data, scenes_data):
        lld = LichtLightsData(lights_data)
        lgd = LichtGroupsData(groups_data)
        lsd = LichtScenesData(scenes_data)
        return cls(lld, lgd, lsd)

    def subset_wrapper(self, subset_clsfunc, attrname, fetcher_funcname):
        attr = self.__getattribute__(attrname)

        def func(*args, **kwargs):
            obj = subset_clsfunc(*args, **kwargs)
            if hasattr(obj, fetcher_funcname):
                attr_index = obj.__getattribute__(fetcher_funcname)
                attr_ids = [ids for index_list in attr_index.values() for ids in index_list]
            elif hasattr(attr, fetcher_funcname):
                attr_index = attr.__getattribute__(fetcher_funcname)(*obj.index)
                attr_ids = attr_index.index
            setattr(obj.__class__, attrname,
                    property(lambda self: attr.subset(attr_ids)))
            return obj
        func.__name__ = subset_clsfunc.__name__
        return func

    def __post_init__(self):
        LichtGroupsData.subset = \
            self.subset_wrapper(LichtGroupsData.subset,
                                'lights', 'lights_index')
        LichtGroupsData.subset = \
            self.subset_wrapper(LichtGroupsData.subset,
                                'scenes', 'in_groups')
        LichtScenesData.subset = \
            self.subset_wrapper(LichtScenesData.subset,
                                'lights', 'lights_index')
        LichtScenesData.subset = \
            self.subset_wrapper(LichtScenesData.subset,
                                'groups', 'group_index')

    def from_path(self, path):
        obj = self
        for p in path.split("/"):
            if hasattr(obj, p):
                obj = obj.__getattribute__(p)
            if p in obj:
                obj = obj.subset([p])
        return obj
