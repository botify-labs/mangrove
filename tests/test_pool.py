import unittest

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
        
