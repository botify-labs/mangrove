import unittest

from concurrent.futures import ThreadPoolExecutor

from boto.s3.connection import S3Connection
from moto import mock_s3, mock_ec2

from mangrove.pool import ServicePool, ServiceMixinPool
from mangrove.mappings import ConnectionsMapping
from mangrove.exceptions import NotConnectedError


class DummyS3Pool(ServicePool):
    _aws_module_name = 's3'


class DummyMixinPool(ServiceMixinPool):
    _aws_services = {
        's3': {
            'regions': ['us-east-1', 'eu-west-1'],
            'default_region': 'us-east-1'
        },
        'ec2': {
            'regions': '*',
            'default_region': 'eu-west-1'
        }
    }


class TestServicePool(unittest.TestCase):
    def test_init_with_connect_flag_set_to_false_has_no_connections(self):
        pool = DummyS3Pool(connect=False)
        self.assertEqual(pool._connections, ConnectionsMapping())

    def test_pool_method_call_with_connect_to_false_raises(self):
        pool = DummyS3Pool(connect=False)

        with self.assertRaises(NotConnectedError):
            pool.region('us-east-1').get_all_buckets()

    def test_pool_regions_are_set_according_to_init_params(self):
        pool = DummyS3Pool(connect=False, regions=['us-east-1', 'eu-west-1'])
        self.assertEqual(pool._regions_names, set(['us-east-1', 'eu-west-1']))
        self.assertEqual(pool._connections.keys(), [])

    @mock_s3
    def test_pool_regions_are_connected_according_to_init_params(self):
        pool = DummyS3Pool(connect=True, regions=['us-east-1', 'eu-west-1'])
        self.assertEqual(pool._regions_names, set(['us-east-1', 'eu-west-1']))
        self.assertEqual(pool._connections.keys(), ['us-east-1', 'eu-west-1'])

    @mock_s3
    def test_add_region_actually_sets_up_region_connection(self):
        pool = DummyS3Pool(connect=True, regions=['us-east-1'])
        self.assertEqual(pool._regions_names, set(['us-east-1']))

        pool.add_region('eu-west-1')
        self.assertEqual(pool._regions_names, set(['us-east-1', 'eu-west-1']))
        self.assertTrue(isinstance(pool._connections['eu-west-1'], S3Connection))


class TestServiceMixinPool(unittest.TestCase):
    @mock_s3
    @mock_ec2
    def test_valid_mixin_pool_instanciation(self):
        pool = DummyMixinPool(connect=False)

        self.assertTrue('s3' in pool.services)
        self.assertTrue('ec2' in pool.services)

        self.assertTrue(pool.s3._regions_names == set(['us-east-1', 'eu-west-1']))
        self.assertTrue(pool.s3._default_region_name == 'us-east-1')
        self.assertTrue(len(pool.ec2._regions_names) > 0)
        self.assertTrue(pool.ec2._default_region_name == 'eu-west-1')

    @mock_s3
    @mock_ec2
    def test_mixin_pool_with_default_region_but_no_regions_provided_raises(self):
        class RaisingMixinPool(ServiceMixinPool):
            _aws_services = {
                's3': {
                    'default_region': 'us-east-1'
                }
            }

        with self.assertRaises(KeyError):
            pool = RaisingMixinPool(connect=False)

    @mock_s3
    @mock_ec2
    def test_mixin_pool_with_default_region_not_part_of_regions_raises(self):
        class RaisingMixinPool(ServiceMixinPool):
            _aws_services = {
                's3': {
                    'regions': ['eu-west-1'],
                    'default_region': 'us-east-1'
                }
            }

        with self.assertRaises(ValueError):
            pool = RaisingMixinPool(connect=False)

    @mock_s3
    @mock_ec2
    def test_mixin_pool_with_invalid_regions_string_raises(self):
        class RaisingMixinPool(ServiceMixinPool):
            _aws_services = {
                's3': {
                    'regions': 'abc 123',
                    'default_region': 'us-east-1'
                }
            }

        with self.assertRaises(ValueError):
            pool = RaisingMixinPool(connect=False)
