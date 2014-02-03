import unittest

from boto.s3.connection import S3Connection
from moto import mock_s3

from mangrove.pool import ServicePool
from mangrove.exceptions import NotConnectedError


class DummyS3Pool(ServicePool):
    _aws_module_name = 's3'


class TestServicePool(unittest.TestCase):
    def test_init_with_connect_flag_set_to_false_has_no_connections(self):
        pool = DummyS3Pool(connect=False)
        self.assertEqual(pool._connections, {})

    def test_pool_method_call_with_connect_to_false_raises(self):
        pool = DummyS3Pool(connect=False)
        
        with self.assertRaises(NotConnectedError):
            pool.region('us-east-1').get_all_buckets()
        
    def test_pool_regions_are_set_according_to_init_params(self):
        pool = DummyS3Pool(connect=False, regions=['us-east-1', 'eu-west-1'])
        self.assertEqual(pool.regions, set(['us-east-1', 'eu-west-1']))
        self.assertEqual(pool._connections.keys(), [])

    @mock_s3
    def test_pool_regions_are_connected_according_to_init_params(self):
        pool = DummyS3Pool(connect=True, regions=['us-east-1', 'eu-west-1'])
        self.assertEqual(pool.regions, set(['us-east-1', 'eu-west-1']))
        self.assertEqual(pool._connections.keys(), ['us-east-1', 'eu-west-1'])

    @mock_s3
    def test_add_region_actually_sets_up_region_connection(self):
        pool = DummyS3Pool(connect=True, regions=['us-east-1'])
        self.assertEqual(pool.regions, set(['us-east-1']))

        pool.add_region('eu-west-1')
        self.assertEqual(pool.regions, set(['us-east-1', 'eu-west-1']))
        self.assertTrue(isinstance(pool._connections['eu-west-1'], S3Connection))
