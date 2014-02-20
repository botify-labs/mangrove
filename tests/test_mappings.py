import unittest
import boto

from concurrent.futures import ThreadPoolExecutor
from moto import mock_s3

from mangrove.mappings import ConnectionsMapping


class TestConnectionsMapping(unittest.TestCase):
    def test_getitem_evaluates_future_connexion(self):
        executor = ThreadPoolExecutor(max_workers=1)
        f = executor.submit(lambda: 1 + 1)

        collection = ConnectionsMapping()
        collection['eu-west-1'] = f

        # If succesfull, an int should be returned rather
        # than a Future.
        value = collection['eu-west-1']  # Calls collection __getitem__
        self.assertTrue(isinstance(value, int))
        self.assertTrue(value == 2)

    def test_getitem_protects_its_classic_behavior_with_common_types(self):
        collection = ConnectionsMapping()
        collection['eu-west-1'] = 2

        # Make sure __getitem__ has the classic behavior
        value = collection['eu-west-1']  # Calls collection __getitem__
        self.assertTrue(isinstance(value, int))
        self.assertTrue(value == 2)

    def test_set_default_with_not_existing_connection_raises(self):
        collection = ConnectionsMapping()

        with self.assertRaises(ValueError):
            collection.default = 'abc 123'

    def test_set_default_with_invalid_type_raises(self):
        collection = ConnectionsMapping()

        with self.assertRaises(TypeError):
            collection.default = 123

    @mock_s3
    def test_set_default_with_valid_connection(self):
        collection = ConnectionsMapping()
        collection['eu-west-1'] = boto.connect_s3()

        collection.default = 'eu-west-1'

        self.assertTrue(collection._default_name is not None)
        self.assertTrue(collection._default_name == 'eu-west-1')
        self.assertTrue(collection.default is not None)
        self.assertTrue(isinstance(collection.default, boto.connection.AWSAuthConnection))
