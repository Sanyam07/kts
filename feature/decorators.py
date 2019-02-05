from ..storage import source_utils
from ..storage.caching import cache
from .. import config
from .storage import FeatureConstructor
from IPython.display import display
from glob import glob
import os

def test(df, sizes=[2, 4, 6]):
    """
    Applies function to heads of particular dataframe.
    
    Example:
    ``` python
    @test(df, sizes=[5, 15])
    def make_ohe_pclass(df):
        ...
    ```
    """
    def __test(function):

        config.test_call = 1
        for sz in sizes:
            display(function(df.head(sz)))
        config.test_call = 0
    
    return __test


def register(*args, cache_default=True):
    """
    Registers function for further caching its calls and restoring source.
    
    Example:
    ``` python
    @register
    def make_ohe_pclass(df):
        ...
    ```
    """

    def __register(func):
        if source_utils.source_is_saved(func) and not source_utils.matches_cache(func):
            raise NameError("A function with the same name is already registered")

        functor = FeatureConstructor(func, cache_default)
        if not source_utils.source_is_saved(func):
            cache.cache_obj(functor, functor.__name__)
            source_utils.save_source(func)
        return functor

    if args:
        function = args[0]
        return __register(function)
    else:
        return __register


def deregister(name, force=False):
    """
    Deletes sources and cached calls of a certain function.
    The interface is too rich now:

    ``` python
    @deregister
    def make_new_features(df):
        ...

    @deregister(force=False)
    def make_new_features(df):
        ...

    deregister('make_new_features', force=False)

    @deregister(force=True)
    def make_new_features(df):
        ...

    deregister('make_new_features', force=True)
    ```

    It's highly recommended to use only `deregister('function_name')` interface.
    Other ones are deprecated.
    """
    confirmation = ''
    if not force:
        print("Are you sure you want to delete all the cached files?")
        print("To confirm please print full name of the function:")
        confirmation = input()
    if not force and confirmation != name:
        print("Doesn't match")
        return

    paths = glob(config.feature_path + name + '.*') + glob(
        config.feature_path + name + '__[0-9a-f][0-9a-f][0-9a-f][0-9a-f].*')
    for path in paths:
        print(f'removing {path}')
        os.remove(path)


def dropper(function):
    """
    Registers function that won't be cached.
    Is recommended to be used only with functions which actually drop columns or rows and don't produce any new data.
    
    Example:
    ``` python
    @dropper
    def drop_pclass(df):
        return stl.column_dropper(['Pclass'])(df)
    ```
    """
#     TODO:
#     if cache.is_cached(function.__name__):
#         print('Dropper is already registered. Deregistering: ')
#         deregister(function.__name__, force=True)
    deregister(function.__name__, force=True)
    return register(function, cache_default=False)


def selector(function):
    """
    Registers function that won't be cached.
    Is recommended to be used only with functions which actually select columns or rows and don't produce any new data.
    
    Example:
    ``` python
    @selector
    def select_pclass_cabin(df):
        return stl.column_selector(['Pclass', 'Cabin'])(df)
    ```
    """
    
    deregister(function.__name__, force=True)
    return register(function, cache_default=False)

