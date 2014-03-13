import types

from mangrove.utils import get_boto_module
from mangrove.constants import WILDCARD_ALL_REGIONS
from mangrove.exceptions import InvalidServiceError, DoesNotExistError


class ServiceDescription(object):
    def __init__(self, description=None):
        self._module = None
        self._service_name = None
        self._regions = []
        self._default_region = None

        if description is not None:
            self.load(description)

    def load(self, description):
        if isinstance(description, str) is True:
            self.from_string(description)
        elif isinstance(description, dict) is True:
            self.from_dict(description)
        else:
            raise TypeError(
                "Unhandle description type. Expected string or dict, "
                "{} found".format(type(description))
            )

    def from_string(self, description):
        if not isinstance(description, str):
            raise TypeError(
                "description parameter has to be of type str, "
                "got {} instead.".format(type(description))
            )

        self.service_name = description
        self.regions = WILDCARD_ALL_REGIONS

    def from_dict(self, description):
        if not isinstance(description, dict):
            raise TypeError(
                "description parameter has to be of type dict, "
                "got {} instead.".format(type(description))
            )

        self.service_name = description.keys()[0]
        self.regions = description[self.service_name].get('regions')
        self.default_region = description[self.service_name].get('default_region')
        

    @property
    def module(self):
        if self.service_name or self._module is not None:
            self._module = get_boto_module(self.service_name)
            return self._module

        return None

    @property
    def service_name(self):
        return self._service_name

    @service_name.setter
    def service_name(self, value):
        try:
            self._module = get_boto_module(value)
        except InvalidServiceError:
            raise
        else:
            self._service_name = value

    @property
    def regions(self):
        return self._regions

    @regions.setter
    def regions(self, value):
        if not isinstance(value, (list, str, types.NoneType)):
            raise TypeError(
                "regions attribute has to be of list or str type, "
                "got {} instead".format(type(value))
            )

        if isinstance(value, str):
            # If a string was supplied as regions value, make sure
            # the string is a wildcard, and the module property is set
            if value != WILDCARD_ALL_REGIONS:
                raise ValueError("Invalid value provided for regions attribute")
            if not self.module:
                raise ValueError("service_name attribute must be set before regions")
            self._regions = [r.name for r in self.module.regions()]
        elif isinstance(value, list):
            if len(value) == 1 and value[0] == WILDCARD_ALL_REGIONS:
                # If regions == ['*'] recrusively call the regions 
                # regions setter with '*' value.
                return setattr(self, 'regions', value[0])
            self._regions = value
        else:
            self._regions = value

    @property
    def default_region(self):
        return self._default_region

    @default_region.setter
    def default_region(self, value):
        if value is not None and not value in self.regions:
            raise DoesNotExistError("supplied region not found to be part of regions attribute")
        self._default_region = value

class ServicePoolDescription(dict):
    def __init__(self, *args, **kwargs):
        pass
