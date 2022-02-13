"""
licht.data

@author: phdenzel
"""
from typing import ClassVar
from dataclasses import dataclass


@dataclass
class LichtProtoData:
    fetch_data: dict = None
    _name: ClassVar = ''

    def __getitem__(self, item):
        if item in self.fetch_data:
            return self.fetch_data[item]

    def __iter__(self):
        if self.fetch_data:
            return self.fetch_data.__iter__()
        return iter([])

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
        return self.__class__({i: self[i] for i in set_list})


@dataclass
class LichtLightsData(LichtProtoData):
    _name: ClassVar = 'lights'


@dataclass
class LichtGroupsData(LichtProtoData):
    _name: ClassVar = 'groups'

    @property
    def lights_index(self):
        return {i: self[i]['lights'] for i in self if 'lights' in self[i]}

    def with_lights(self, *lights_ids):
        group_ids = [i for i, li in self.lights_index.items()
                     if all(lij in li for lij in lights_ids)]
        return self.subset(group_ids)


@dataclass
class LichtScenesData(LichtProtoData):
    _name: ClassVar = 'scenes'

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
