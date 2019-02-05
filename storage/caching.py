from . import cache_utils
from .. import config
import datetime
from glob import glob
import os
from .info import info


class Cache:
    """
    Standard interface for lru caching DataFrames and objects
    """

    def __init__(self):
        self.__memory = dict()
        self.last_used = dict()
        self.current_volume = 0
        try:
            _ = info.memory_limit  # to check whether it exists
        except Exception:
            info.memory_limit = 4 * (1024 ** 3)  # 4 Gb

    @staticmethod
    def set_memory_limit(volume):
        """
        Sets new memory limit
        :param volume: new memory volume limit
        :return:
        """
        info.memory_limit = volume

    def __release_volume(self, df):
        """
        Removes most unpopular dataframes until it is possible to cache given one
        :param df: dataframe
        :return:
        """

        items = sorted([(time, key) for (key, time) in self.last_used.items()])
        cur = 0
        while self.current_volume + cache_utils.get_df_volume(df) > info.memory_limit:
            key = items[cur][1]
            cur += 1
            self.current_volume -= cache_utils.get_df_volume(self.__memory[key])
            self.__memory.pop(key)
            self.last_used.pop(key)

    def is_cached_df(self, name):
        """
        Checks whether df is in cache
        :param name: name of frame
        :return: True or False (cache hit or miss)
        """
        dict_name = name + '_df'
        return dict_name in self.__memory or os.path.exists(cache_utils.get_path_df(name))

    def cache_df(self, df, name):
        """
        Caches dataframe with given name
        :param df: object
        :param name: object name
        :return:
        """
        if self.is_cached_df(name):
            return
        if cache_utils.get_df_volume(df) > info.memory_limit:
            raise MemoryError

        dict_name = name + '_df'
        self.__release_volume(df)
        self.__memory[dict_name] = df
        self.current_volume += cache_utils.get_df_volume(df)
        self.last_used[dict_name] = datetime.datetime.now()
        cache_utils.save_df(df, cache_utils.get_path_df(name))

    def load_df(self, name):
        """
        Loads dataframe from cache
        :param name: name of object
        :return: dataframe with given name
        """
        if not self.is_cached_df(name):
            raise KeyError("No such df in cache")

        dict_name = name + '_df'
        self.last_used[dict_name] = datetime.datetime.now()
        if dict_name in self.__memory:
            return self.__memory[dict_name]
        else:
            tmp = cache_utils.load_df(cache_utils.get_path_df(name))
            self.__release_volume(tmp)
            self.__memory[dict_name] = tmp
            return tmp

    @staticmethod
    def cached_dfs():
        """
        Returns list of cached dataframes
        :return:
        """
        return [df.split('/')[-1][:-3] for df in
                glob(config.storage_path + '*' + '__[0-9a-f][0-9a-f][0-9a-f][0-9a-f]_df')]

    def is_cached_obj(self, name):
        """
        Checks whether obj is in cache
        :param name: name of file
        :return: True or False (chache hit or miss)
        """
        dict_name = name + '_obj'
        return dict_name in self.__memory or os.path.exists(cache_utils.get_path_obj(name))

    def cache_obj(self, obj, name):
        """
        Caches object with given name
        :param obj: object
        :param name: object name
        :return:
        """
        if self.is_cached_obj(name):
            return

        dict_name = name + '_obj'
        self.__memory[dict_name] = obj
        cache_utils.save_obj(obj, cache_utils.get_path_obj(name))

    def load_obj(self, name):
        """
        Loads object from cache
        :param name: name of object
        :return: object with given name
        """
        if not self.is_cached_obj(name):
            raise KeyError("No such object in cache")

        dict_name = name + '_obj'
        if dict_name in self.__memory:
            return self.__memory[dict_name]
        else:
            tmp = cache_utils.load_obj(cache_utils.get_path_obj(name))
            self.__memory[dict_name] = tmp
            return tmp

    @staticmethod
    def cached_objs():
        """
        Returns list of cached
        :return:
        """
        return [df.split('/')[-1][:-4] for df in
                glob(config.storage_path + '*' + '_obj')]


cache = Cache()
