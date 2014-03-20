import types

from mangrove.utils import get_boto_module
from mangrove.constants import WILDCARD_ALL_REGIONS
from mangrove.exceptions import InvalidServiceError, DoesNotExistError


class ServiceDeclaration(object):
    def __init__(self, declaration=None):
        self._module = None
        self._service_name = None
        self._regions = []
        self._default_region = None

        if declaration is not None:
            self.load(declaration)

    def load(self, declaration):
        if isinstance(declaration, str) is True:
            self.from_string(declaration)
        elif isinstance(declaration, dict) is True:
            self.from_dict(declaration)
        else:
            raise TypeError(
                "Unhandle declaration type. Expected string or dict, "
                "{} found".format(type(declaration))
            )

    def from_string(self, declaration):
        if not isinstance(declaration, str):
            raise TypeError(
                "declaration parameter has to be of type str, "
                "got {} instead.".format(type(declaration))
            )

        self.service_name = declaration
        self.regions = WILDCARD_ALL_REGIONS

    def from_dict(self, declaration):
        if not isinstance(declaration, dict):
            raise TypeError(
                "declaration parameter has to be of type dict, "
                "got {} instead.".format(type(declaration))
            )

        self.service_name = declaration.keys()[0]
        self.regions = declaration[self.service_name].get('regions')
        self.default_region = declaration[self.service_name].get('default_region')
        

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
        if value is not None:
            if self.regions is None or value not in self.regions:
                raise ValueError("supplied region not found to be part of regions attribute")

        self._default_region = value

class ServicePoolDeclaration(dict):
    def __init__(self, declaration=None):
        super(ServicePoolDeclaration, self).__init__()

        if declaration is not None:
            self.from_dict(declaration)

    def from_dict(self, declaration):
        for service_name, localisation in declaration.iteritems():
            self[service_name] =  ServiceDeclaration({service_name: localisation})
