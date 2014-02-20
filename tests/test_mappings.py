import unittest

from concurrent.futures import ThreadPoolExecutor

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
