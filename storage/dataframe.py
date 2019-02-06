import pandas as pd
from copy import deepcopy


class DataFrame(object):
    """
    A wrapper over the standard DataFrame class.
    Complements it with .train and .encoders attributes.

    This class is implemented to supply an indicator
    for functions whether they serve a train or test call and let propagate
    this indicator further to inner functions.

    Returns kts.DataFrame from any attribute that produces pd.DataFrame,
    but kts.DataFrame.drop([]) will return pd.DataFrame.
    That's not a bug, as `a(b(df))` will still propagate
    aforementioned signal, but `a(b(df.drop()))` construction is not to be
    registered as a cached function.

    Example:
    ```
    def a(df):
        res = stl.empty_like(df)
        tmp = b(df)
        res['res'] = b['b'] ** 2
        return res
    ```
    """
    def __init__(self, df, train=False, encoders=dict()):
        # print('making custom DF', type(df))
        if isinstance(df, DataFrame):
            # print('out of custom')
            super().__setattr__('df', df.df)
            super().__setattr__('train', df.train)
            super().__setattr__('encoders', df.encoders) # not deepcopy to allow DF(df) init in FeatureConstructors
        else:
            # print('out of std')
            super().__setattr__('df', df)
            super().__setattr__('train', train)
            super().__setattr__('encoders', encoders)

    def __copy__(self):
        return DataFrame(self.df, self.train, deepcopy(self.encoders))

    def __getattr__(self, key):
        if key in ['train', 'encoders', 'df']:
            return super().__getattr__(key)
        else:
            tmp = self.df.__getattr__(key)
            if isinstance(tmp, pd.DataFrame):
                return DataFrame(tmp, self.train, self.encoders)
            else:
                return tmp

    def __setattr__(self, key, value):
        if key in ['train', 'encoders', 'df']:
            super().__setattr__(key, value)
        else:
            self.df.__setattr__(key, value)

    def __setitem__(self, key, value):
        self.df.__setitem__(key, value)

    def __getitem__(self, key):
        tmp = self.df.__getitem__(key)
        if isinstance(tmp, pd.DataFrame):
            return DataFrame(tmp, self.train, self.encoders)
        else:
            return tmp
