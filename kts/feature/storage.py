from .. import config
from ..storage import source_utils
from ..storage import cache_utils
from ..storage import caching
from ..storage import dataframe
import glob
import os
import numpy as np


class FeatureConstructor:
    def __init__(self, function, cache_default=True):
        self.function = function
        self.cache_default = cache_default
        self.__name__ = function.__name__
        self.source = source_utils.get_source(function)
        self.stl = False

    # needs refactoring because of direct storing source
    def __call__(self, df, cache=None, **kwargs):
        # print("before constr", df.train)
        ktdf = dataframe.DataFrame(df)  # TODO: uncomment this line after tests with @preview
        # print("after constr:", ktdf.train)
        if type(cache) == type(None):
            cache = self.cache_default
        if not cache or config.preview_call:  # dirty hack to avoid  caching when @test function uses @registered function inside
            return self.function(ktdf, **kwargs)

        name = f"{self.function.__name__}__{cache_utils.get_hash_df(ktdf)[:4]}__{ktdf.slice_id[-4:]}"
        if caching.cache.is_cached_df(name):
            # return caching.cache.load_df(name)
            return dataframe.DataFrame(caching.cache.load_df(name), ktdf.train, ktdf.encoders)
        else:
            result = self.function(ktdf)
            caching.cache.cache_df(result, name)
            # return result
            return dataframe.DataFrame(result, ktdf.train, ktdf.encoders)

    def __repr__(self):
        return f'<Feature Constructor "{self.__name__}">'

    def __str__(self):
        return self.__name__


from . import stl

class FeatureSet:
    def __init__(self, fc_before, fc_after=stl.empty_like, df_input=None, target_column=None, encoders={}):
        self.fc_before = fc_before
        self.fc_after = fc_after
        self.target_column = target_column
        self.encoders = encoders
        if type(df_input) != type(None):
            self.set_df(df_input)
        self.__name__ = f"fs({self.fc_before.__name__[:2]}-{self.fc_after.__name__[:2] if self.fc_after else ''})"

    def set_df(self, df_input):
        self.df_input = dataframe.DataFrame(df_input)
        self.df_input.train = True
        self.df_input.encoders = self.encoders
        self.df = self.fc_before(self.df_input)
        
    def __call__(self, df):
        ktdf = dataframe.DataFrame(df)
        ktdf.encoders = self.encoders
        return stl.merge([
            self.fc_before(ktdf),
            self.fc_after(ktdf)
        ])
        
    def __getitem__(self, idx):
        if isinstance(self.df_input, type(None)):
            raise AttributeError("Input DataFrame is not defined")
        return stl.merge([
            self.df.iloc[idx], 
            self.fc_after(dataframe.DataFrame(self.df_input.iloc[idx], train=1))  # BUG: should have .train=True?
        ])                                                                        # made .train=1 only for preview purposes
                                                                                  # actually, FS[a:b] functionality is made only for debug
                                                                                  # why not write config.preview_call = 1 then?
    def empty_copy(self):
        return FeatureSet(self.fc_before, 
                          self.fc_after,
                          target_column=self.target_column,
                          encoders=self.encoders
                         )

    def slice(self, idxs):
        return FeatureSlice(self, idxs)

    @property
    def target(self):
        if self.target_column:
            return self.df_input[self.target_column]
        else:
            raise AttributeError("Target column is not defined.")

    @property
    def source(self):
        raise NotImplementedError
        used_funcs = (self.features_before + self.features_after)[::-1]
        for func in used_funcs:
            for func_stored in feature_list:
                if func_stored.__name__ in func.source and \
                func_stored.__name__ not in [i.__name__ for i in used_funcs]:
                    used_funcs.append(func_stored)
        src = '\n'.join([i.source for i in used_funcs[::-1]]) 
        
        src += '\n\n'
#         src += inspect.getsource(type(self))
#         src += '\n\n'
        src += 'featureset = '
        src += type(self).__name__ + '('
        src += 'features_before=[' + ', '.join([i.__name__ for i in self.features_before]) + '], '
        src += 'features_after=[' + ', '.join([i.__name__ for i in self.features_after]) + ']'
        src += ')'
        return src


class FeatureSlice:
    def __init__(self, featureset, slice):
        self.featureset = featureset
        self.slice = slice
        self.slice_id = cache_utils.get_hash_slice(slice)
        self.first_level_encoders = self.featureset.encoders
        self.second_level_encoders = {}
        self.columns = None
        # self.df_input = copy(self.featureset.df_input)

    def __call__(self, df=None):
        if isinstance(df, type(None)):
            fsl_level_df = dataframe.DataFrame(self.featureset.df_input.iloc[self.slice],  # ALERT: may face memory leak here
                                               slice_id=self.slice_id,
                                               train=True,
                                               encoders=self.second_level_encoders)
            result = stl.merge([
                self.featureset.df.iloc[self.slice],
                self.featureset.fc_after(fsl_level_df)
            ])
            self.columns = [i for i in result.columns if i != self.featureset.target_column]
            return result[self.columns]
        elif isinstance(df, slice) or isinstance(df, np.ndarray) or isinstance(df, list):
            fsl_level_df = dataframe.DataFrame(self.featureset.df_input.iloc[df],  # ALERT: may face memory leak here
                                               slice_id=self.slice_id,
                                               train=False,
                                               encoders=self.second_level_encoders)
            result = stl.merge([
                self.featureset.df.iloc[df],
                self.featureset.fc_after(fsl_level_df)
            ])
            self.columns = [i for i in result.columns if i != self.featureset.target_column]
            return result[self.columns]
        else:
            fs_level_df = dataframe.DataFrame(df)
            fs_level_df.encoders = self.first_level_encoders
            fsl_level_df = dataframe.DataFrame(df)
            fsl_level_df.encoders = self.second_level_encoders
            fsl_level_df.slice_id = self.slice_id
            return stl.merge([
                self.featureset.fc_before(fs_level_df),  # uses FeatureSet-level encoders
                self.featureset.fc_after(fsl_level_df)  # uses FeatureSlice-level encoders
            ])[self.columns]

    @property
    def target(self):
        return self.featureset.target.iloc[self.slice]

    def compress(self):
        self.featureset = self.featureset.empty_copy()

    
from collections import MutableSequence

class FeatureList(MutableSequence):
    def __init__(self):
        self.full_name = "kts.feature.storage.feature_list"  # such a hardcode
        self.names = [self.full_name]
        while self.names[-1].count('.'):
            self.names.append(self.names[-1][self.names[-1].find('.') + 1:])
        self.functors = []
        self.name_to_idx = dict()

    def recalc(self):
        self.functors = []
        self.name_to_idx = dict()
        files = glob.glob(config.storage_path + '*_fc_obj')
        files.sort(key=os.path.getmtime)
        files = [file.split('/')[-1] for file in files]
        for idx, file in enumerate(files):
            functor = caching.cache.load_obj(file[:-4])
            self.functors.append(functor)
            self.name_to_idx[functor.__name__] = idx

    def __repr__(self):
        self.recalc()
        string = f"[{', '.join([f.__str__() for f in self.functors])}]"
        return string

    def __getitem__(self, key):
        self.recalc()
        if type(key) in [int, slice]:
            return self.functors[key]
        elif type(key) == str:
            return self.functors[self.name_to_idx[key]]
        else:
            raise TypeError('Index should be int, slice or str')

    def __delitem__(self, key):
        raise AttributeError('This object is read-only')

    def __setitem__(self, key, value):
        raise AttributeError('This object is read-only')

    def insert(self, key, value):
        raise AttributeError('This object is read-only')

    def define_in_scope(self, global_scope):
        self.recalc()
        for func in self.name_to_idx:
            for name in self.names:
                try:
                    exec(f"{func} = {name}['{func}']", global_scope)
                    break
                except BaseException:
                    pass

    def __len__(self):
        self.recalc()
        return len(self.functors)


feature_list = FeatureList()