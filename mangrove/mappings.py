from boto.connection import AWSAuthConnection
from concurrent.futures._base import Future


class ConnectionsMapping(dict):
    """Exposes a region name to connection mapping

    If connection is a future, it's evaluated value will
    be returned. Be aware it could potentially block.

    :param  default: name of the region to be set as default
    :type   default: string
    """
    def __init__(self, default=None, *args, **kwargs):
        super(ConnectionsMapping, self).__init__(*args, **kwargs)
        self._default_name = default

    @property
    def default(self):
        if not hasattr(self, '_default'):
            self._default = None

        if self._default_name is not None:
            if self._default_name in self:
                self._default = self.__getitem__(self._default_name)

        return self._default

    @default.setter
    def default(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise TypeError(
                    "default attribute value should be a string. "
                    "Got {} instead.".format(type(value))
                )
            elif value not in self:
                raise ValueError("{} region connection not found".format(value))

        self._default_name = value
        self._default = self.__getitem__(value)

    def __getitem__(self, key):
        """Gets value from mapping key

        If the found value is a Future it's evaluation (using the result() method)
        is returned. Be aware it could potentially block.

        :param  key: key to fetch value from in the mapping
        :type   key: string
        """
        value = dict.__getitem__(self, key)

        if isinstance(value, Future):
            value = value.result()
            dict.__setitem__(self, key, value)

        return value
