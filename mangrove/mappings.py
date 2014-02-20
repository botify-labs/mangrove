from concurrent.futures._base import Future


class ConnectionsMapping(dict):
    """Exposes a region name to connection mapping

    If connection is a future, it's evaluated value will
    be returned. Be aware it could potentially block.
    """
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
