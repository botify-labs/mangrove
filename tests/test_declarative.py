import pytest
import types

from boto import ec2
from moto import mock_ec2, mock_s3

from mangrove.declarative import ServiceDeclaration, ServicePoolDeclaration
from mangrove.constants import WILDCARD_ALL_REGIONS
from mangrove.exceptions import InvalidServiceError, DoesNotExistError


class TestServiceDeclaration:
    @mock_ec2
    def test_from_string_with_a_valid_service_name_declaration(self):
        sd = ServiceDeclaration()
        sd.from_string('ec2')
        expected_regions = [r.name for r in ec2.regions()]

        assert sd.service_name == 'ec2'
        assert sd.regions == expected_regions

    def test_from_string_with_an_invalid_service_name_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(InvalidServiceError):
            sd.from_string('ec3')

    def test_from_string_with_an_invalid_type_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(TypeError):
            sd.from_string(123)

    @mock_ec2
    def test_from_dict_with_a_valid_declaration(self):
        sd = ServiceDeclaration()
        sd.from_dict({
            'ec2': {
                'regions': ['eu-west-1', 'us-east-1'],
                'default_region': 'eu-west-1'
            }
        })

        assert sd.service_name == 'ec2'
        assert sd.regions == ['eu-west-1', 'us-east-1']
        assert sd.default_region == 'eu-west-1'

    def test_from_dict_with_an_invalid_service_name_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(InvalidServiceError):
            sd.from_dict({'ec3': {}})

    def test_from_dict_with_invalid_declaration_type_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(TypeError):
            sd.from_dict(123)

    def test_from_string_with_an_invalid_service_name_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(InvalidServiceError):
            sd.from_string('ec3')

    def test_module_getter_without_service_name_is_none(self):
        sd = ServiceDeclaration()

        assert sd.service_name is None
        assert sd.module is None

    def test_module_getter_with_invalid_service_name(self):
        sd = ServiceDeclaration()

        with pytest.raises(InvalidServiceError):
            sd.service_name = 'ec3'
            sd.module

    def test_module_getter_with_valid_service_name(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'

        assert sd.module is not None
        assert isinstance(sd.module, types.ModuleType)

    def test_service_name_setter_raises_with_non_existing_boto_module(self):
        sd = ServiceDeclaration()

        with pytest.raises(InvalidServiceError):
            sd.service_name = 'ec3'

    def test_regions_setter_raises_with_invalid_type(self):
        sd = ServiceDeclaration()

        with pytest.raises(TypeError):
            sd.regions = 123

    def test_regions_setter_with_non_wildcard_string_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(ValueError):
            sd.regions = 'abc'

    def test_regions_setter_with_wildcard_but_unset_module_raises(self):
        sd = ServiceDeclaration()

        with pytest.raises(ValueError):
            sd._module = None
            sd.regions = '*'

    @mock_ec2
    def test_regions_setter_with_wildcard_converts_to_regions_list(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = '*'

        expected_regions = [r.name for r in ec2.regions()]
        assert sd.regions == expected_regions

    @mock_ec2
    def test_regions_setter_with_wildcard_list_converts_to_regions_list(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = ['*']

        expected_regions = [r.name for r in ec2.regions()]
        assert sd.regions == expected_regions

    def test_regions_setter_with_regions_list(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = ['us-east-1', 'eu-west-1']

        assert sd.regions == ['us-east-1', 'eu-west-1']

    def test_regions_setter_with_none_value(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = None

        assert sd.regions is None

    def test_default_region_setter_with_empty_regions_raises(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = []

        with pytest.raises(DoesNotExistError):
            sd.default_region = 'us-east-1'

    def test_default_region_setter_with_none_value(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = ['us-east-1']
        sd.default_region = None

        assert sd.default_region is None

    def test_default_region_setter(self):
        sd = ServiceDeclaration()
        sd.service_name = 'ec2'
        sd.regions = ['us-east-1']
        sd.default_region = 'us-east-1'

        assert sd.default_region == 'us-east-1'

    def test_load_invalid_type_raises(self):
        with pytest.raises(TypeError):
            ServiceDeclaration(123)

class TestServicePoolDeclaration:
    @mock_ec2
    @mock_s3
    def test_from_dict_with_valid_declaration(self):
        spd = ServicePoolDeclaration()
        spd.from_dict({
            'ec2': {},
            's3': {
                'region': 'us-east-1',
            }
        })

        assert isinstance(spd['ec2'], ServiceDeclaration) is True
        assert spd['ec2'].service_name == 'ec2'
        assert isinstance(spd['s3'], ServiceDeclaration) is True
        assert spd['s3'].service_name == 's3'

    def test_from_dict_with_invalid_declaration_raises(self):
        spd = ServicePoolDeclaration()

        with pytest.raises(InvalidServiceError):
            spd.from_dict({
                'abc': {
                    '123': 'easy as',
                }
            })
