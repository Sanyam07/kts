import inspect

from kts.core.feature_constructor.parallel import ParallelFeatureConstructor
from kts.core.frame import KTSFrame


class FeatureConstructor(ParallelFeatureConstructor):
    parallel = True
    cache = True

    def __init__(self, func, internal=False):
        self.func = func
        if internal:
            return
        self.name = func.__name__
        self.source = inspect.getsource(func)
        self.dependencies = self.extract_dependencies(func)

    def compute(self, kf: KTSFrame):
        kwargs = {key: self.request_resource(value, kf) for key, value in self.dependencies}
        result = self.func(kf, **kwargs)
        if (not kf.train and '__columns' in kf._state
            and not (len(result.columns) == len(kf._state['__columns'])
                     and all(result.columns == kf._state['__columns']))):
            fixed_columns = kf._state['__columns']
            for col in set(fixed_columns) - set(result.columns):
                result[col] = None
            return result[fixed_columns]
        if '__columns' not in kf._state:
            kf._state['__columns'] = list(kf.columns)
        return result

    def extract_dependencies(self, func):
        dependencies = dict()
        for k, v in inspect.signature(func).parameters.items():
            if isinstance(v.default, str) or isinstance(v.default, int) or isinstance(v.default, bool):
                dependencies[k] = v.default
            elif v.default != inspect._empty:
                raise UserWarning(f"Unknown argument: {k}={repr(v.default)}.")
        return dependencies
