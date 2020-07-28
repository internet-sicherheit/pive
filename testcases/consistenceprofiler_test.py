import unittest

from traceback import print_exc

from pive import consistenceprofiler as cp

class TestConsistenceprofiler(unittest.TestCase):

    def test_is_date(self):
        # ISO-8601 date format
        self.assertTrue(cp.is_date("2020-01-01"))
        self.assertTrue(cp.is_date("2020-01-01T00:00"))

        # Regular string
        self.assertFalse(cp.is_date("foobar"))

        # Strings with code words in Python and JSON
        self.assertFalse(cp.is_date("None"))
        self.assertFalse(cp.is_date("null"))

        # Nulltype
        self.assertFalse(cp.is_date(None))

        # Regular integer
        self.assertFalse(cp.is_date(0))

        # Integer as string
        self.assertFalse(cp.is_date("42"))

        #E mpty string
        self.assertFalse(cp.is_date(""))

    def test_is_float(self):

        # Float input as string
        self.assertTrue(cp.is_float("0.0"))
        self.assertTrue(cp.is_float("-1.0"))
        self.assertTrue(cp.is_float("42"))
        self.assertTrue(cp.is_float("5E20"))

        # float specific edge cases as strings
        self.assertTrue(cp.is_float("-0.0"))
        self.assertTrue(cp.is_float("inf"))  # TODO: Should this fail?
        self.assertTrue(cp.is_float("NaN")) # TODO: Should this fail?

        # non-edge cases as float input
        self.assertTrue(cp.is_float(0.0))
        self.assertTrue(cp.is_float(-0.0))
        self.assertTrue(cp.is_float(-1.0))
        self.assertTrue(cp.is_float(42))

        # regular string
        self.assertFalse(cp.is_float("foobar"))

        # contains decimal separator, but isnt a float
        self.assertFalse(cp.is_float("127.0.0.1"))

        # Strings with code words in Python and JSON
        self.assertFalse(cp.is_float("None"))
        self.assertFalse(cp.is_float("null"))

        # Nulltype
        self.assertFalse(cp.is_float(None))

    def test_is_int(self):

        # integers as intigers
        self.assertTrue(cp.is_int(0))
        self.assertTrue(cp.is_int(42))
        self.assertTrue(cp.is_int(-1))

        #integers as strings
        self.assertTrue(cp.is_int("0"))
        self.assertTrue(cp.is_int("42"))
        self.assertTrue(cp.is_int("-1"))

        # float
        self.assertFalse(cp.is_int(1.1))

        # nulltype
        self.assertFalse(cp.is_int(None))

        # floats as strings
        self.assertFalse(cp.is_int("1.1"))
        self.assertFalse(cp.is_int("inf"))