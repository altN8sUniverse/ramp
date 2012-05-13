from features import BaseFeature, Feature
from utils import _pprint
import copy

class Configuration(object):
    DEFAULT_PREDICTIONS_NAME = '$predictions'
    def __init__(self, target=None, features=None, metric=None, model=None,
            column_subset=None, prediction=None, predictions_name=None,
            actual=None):
        self.set_attrs(target, features, metric, model,
                column_subset, prediction, predictions_name, actual)

    def set_attrs(self, target=None, features=None, metric=None, model=None,
            column_subset=None, prediction=None,
            predictions_name=None, actual=None):
        if prediction is not None:
            if predictions_name is None:
                raise ValueError("If you provide a prediction feature, you "
                "must also specify a _unique_ 'predictions_name'")
        self.target = target if isinstance(target, BaseFeature) or target is None else Feature(target)
        self.prediction = prediction if isinstance(prediction, BaseFeature) or prediction is None else Feature(prediction)
        self.predictions_name = predictions_name
        if actual is None:
            actual = self.target
        self.actual = actual if isinstance(actual, BaseFeature) else Feature(actual)
        self.features = [f if isinstance(f, BaseFeature) else Feature(f) for f
                in features] if features else None
        self.metric = metric
        self.model = model
        self.column_subset = column_subset

    def __repr__(self):
        return '%s(%s)' % (
                self.__class__.__name__,
                _pprint(self.__dict__))

    def __str__(self):
        return '%s\n\tmodel: %s\n\t%d features\n\ttarget: %s' % (
            'Configuration',
            self.model,
            len(self.features),
            self.target
        )
    # @property
    # def storable_hash(self):
    #     return repr(self)

    def update(self, dct):
        d = self.__dict__.copy()
        d.update(dct)
        self.set_attrs(**d)

    def match(self, **kwargs):
        if 'features' in kwargs:
            for f in kwargs['features']:
                if f.unique_name not in [sf.unique_name for sf in self.features]:
                    return False
        if 'target_name' in kwargs:
            if kwargs['target_name'] != self.target.unique_name:
                return False
        if 'metric' in kwargs:
            if kwargs['metric'].__class__ != self.metric.__class__:
                return False
        if 'model' in kwargs:
            if kwargs['model'].__class__!= self.model.__class__:
                return False
        return True

class ConfigFactory(object):
    def __init__(self, base_config, **kwargs):
        self.config = base_config
        self.kwargs = kwargs

    def __iter__(self):
        return self.iterate(self.kwargs, self.config)

    def iterate(self, dct, config):
        if not dct:
            yield config
            return
        dct = copy.copy(dct)
        k, values = dct.popitem()
        if not hasattr(self.config, k):
            raise ValueError("'%s' not a valid configuration parameter"%k)
        for v in values:
            new_config = copy.copy(config)
            new_config.update({k:v})
            for cnf in self.iterate(dct, new_config):
                yield cnf

