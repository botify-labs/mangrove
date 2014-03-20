import pytest

from concurrent.futures import ThreadPoolExecutor

from boto.s3.connection import S3Connection
from moto import mock_s3, mock_ec2

from mangrove.pool import ServicePool, ServiceMixinPool
from mangrove.mappings import ConnectionsMapping
from mangrove.exceptions import NotConnectedError, DoesNotExistError


class DummyS3Pool(ServicePool):
    service = 's3'


class DummyMixinPool(ServiceMixinPool):
    services = {
        's3': {
            'regions': ['us-east-1', 'eu-west-1'],
            'default_region': 'us-east-1'
        },
        'ec2': {
            'regions': '*',
            'default_region': 'eu-west-1'
        }
    }


class TestServicePool:
    def test_init_with_connect_flag_set_to_false_has_no_connections(self):
        pool = DummyS3Pool(connect=False)
        assert pool._connections == ConnectionsMapping()

    def test_pool_method_call_with_connect_to_false_raises(self):
        pool = DummyS3Pool(connect=False)

        with pytest.raises(NotConnectedError):
            pool.region('us-east-1').get_all_buckets()

    def test_pool_regions_are_set_according_to_init_params(self):
        pool = DummyS3Pool(connect=False, regions=['us-east-1', 'eu-west-1'])
        assert pool._service_declaration.regions == ['us-east-1', 'eu-west-1']
        assert pool._connections.keys() == []

    @mock_s3
    def test_pool_regions_are_connected_according_to_init_params(self):
        pool = DummyS3Pool(connect=True, regions=['us-east-1', 'eu-west-1'])
        assert pool._service_declaration.regions == ['us-east-1', 'eu-west-1']
        assert pool._connections.keys() == ['us-east-1', 'eu-west-1']

    @mock_s3
    def test_add_region_actually_sets_up_region_connection(self):
        pool = DummyS3Pool(connect=True, regions=['us-east-1'])
        assert pool._service_declaration.regions == ['us-east-1']

        pool.add_region('eu-west-1')
        assert pool._service_declaration.regions == ['us-east-1', 'eu-west-1']
        assert isinstance(pool._connections['eu-west-1'], S3Connection) is True


class TestServiceMixinPool:
    @mock_s3
    @mock_ec2
    def test_valid_mixin_pool_instanciation(self):
        pool = DummyMixinPool(connect=False)

        assert 's3' in pool.services
        assert 'ec2' in pool.services

        assert pool.s3._regions_names == ['us-east-1', 'eu-west-1']
        assert pool.s3._default_region == 'us-east-1'
        assert len(pool.ec2._regions_names) > 0
        assert pool.ec2._default_region == 'eu-west-1'

    @mock_s3
    @mock_ec2
    def test_mixin_pool_with_default_region_but_no_regions_provided_raises(self):
        class RaisingMixinPool(ServiceMixinPool):
            services = {
                's3': {
                    'default_region': 'us-east-1'
                }
            }

        with pytest.raises(ValueError):
            pool = RaisingMixinPool(connect=False)

    @mock_s3
    @mock_ec2
    def test_mixin_pool_with_default_region_not_part_of_regions_raises(self):
        class RaisingMixinPool(ServiceMixinPool):
            services = {
                's3': {
                    'regions': ['eu-west-1'],
                    'default_region': 'us-east-1'
                }
            }

        with pytest.raises(ValueError):
            pool = RaisingMixinPool(connect=False)

    @mock_s3
    @mock_ec2
    def test_mixin_pool_with_invalid_regions_string_raises(self):
        class RaisingMixinPool(ServiceMixinPool):
            services = {
                's3': {
                    'regions': 'abc 123',
                    'default_region': 'us-east-1'
                }
            }

        with pytest.raises(ValueError):
            pool = RaisingMixinPool(connect=False)
