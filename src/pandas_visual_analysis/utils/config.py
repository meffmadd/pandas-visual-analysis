from pandas_visual_analysis.utils import Singleton


class Config(dict, metaclass=Singleton):

    dict_attributes = set(dir(dict))

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        if attr in self.dict_attributes:
            raise ValueError(
                "Attribute would overwrite dict attributes and cause undefined behaviour."
            )
        self[attr] = value
