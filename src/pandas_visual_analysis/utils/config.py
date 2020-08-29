from pandas_visual_analysis.utils import Singleton


class Config(dict, metaclass=Singleton):

    dict_attributes = set(dir(dict))

    def __getattr__(self, attr):
        """

        :param attr: The attribute to get from the config.
        :return: The value of the attribute.
        """
        return self[attr]

    def __setattr__(self, attr, value):
        """

        :param attr: The attribute to set the value for.
        :param value: The value of the attribute to be stored.
        :return: None
        """
        if attr in self.dict_attributes:
            raise ValueError(
                "Attribute would overwrite dict attributes and cause undefined behaviour."
            )
        self[attr] = value
