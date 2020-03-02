import numpy as np

import kts.ui.components as ui
from kts.util.hashing import hash_dict, hash_str


class TrackingMixin:
    @property
    def params(self):
        try:
            tracked_params = self.tracked_params
        except:
            tracked_params = self.get_tracked_params()
        params = {
            key: self.get_params()[key]
            for key in tracked_params if key in self.get_params()
        }
        return params


class NamingMixin(TrackingMixin):
    @property
    def name(self):
        name = self.__class__.__name__
        name += hash_dict(self.params, 3)
        if 'class_source' in dir(self):
            name += hash_str(self.class_source, 2)
        return name


class SourceMixin(TrackingMixin):
    @property
    def source(self):
        args = []
        for key, value in self.params.items():
            args.append(f"{key}={repr(value)}")
        res = ", ".join(args)
        return f"{self.__class__.__name__}({res})"


class PreprocessingMixin:
    def preprocess(self, X, y=None):
        return X, y

    def preprocess_fit(self, X, y, *args, **kwargs):
        X_proc, y_proc = self.preprocess(X, y)
        self.fit(X_proc, y_proc, *args, **kwargs)

    def preprocess_predict(self, X, *args, **kwargs):
        X_proc, _ = self.preprocess(X, None)
        return self.predict(X_proc, *args, **kwargs)


class ProgressMixin:
    def progress_callback(self, line):
        return {'success': False}

    def enable_verbosity(self):
        pass

    def get_n_steps(self):
        return 1


class HTMLReprMixin(ui.HTMLRepr, TrackingMixin):
    def _html_elements(self):
        from kts.modelling.custom_model import CustomModel
        elements = [
            ui.Annotation('name'),
            ui.Field(self.name),
            ui.Annotation('model'),
            ui.Field(self.__class__.__name__),
            ui.Annotation('params'),
            ui.Field(str(self.params)),
            ui.Annotation('source'),
            ui.Code(self.source)
        ]
        if isinstance(self, CustomModel):
            elements += [
                ui.Annotation('custom model class source'),
                ui.Code(self.class_source)
            ]
        return elements

    @property
    def html(self):
        return ui.Column([ui.Title('model')] + self._html_elements()).html

    @property
    def html_collapsible(self):
        css_id = np.random.randint(1000000000)
        elements = [ui.TitleWithCross('model', css_id)]
        elements += self._html_elements()
        return ui.CollapsibleColumn(elements, ui.ThumbnailField('model', css_id), css_id).html


class Model(NamingMixin, SourceMixin, PreprocessingMixin, ProgressMixin, HTMLReprMixin):
    pass


class BinaryClassifierMixin(Model):
    def predict(self, X, **kwargs):
        return self.predict_proba(X, **kwargs)[:, 1]


class MultiClassifierMixin(Model):
    def predict(self, X, **kwargs):
        return self.predict_proba(X, **kwargs)


class RegressorMixin(Model):
    pass
