import unittest

from traceback import print_exc

from pive import visualizationmapper as mapper


class TestVisualisationMapper(unittest.TestCase):

    def test_types_matching_data_requirements(self):
        #No requirements
        self.assertTrue(mapper.types_matching_data_requirements([], []))

        #Requirements simplified to numbers instead of types, overlap in 3
        self.assertTrue(mapper.types_matching_data_requirements([{1, 2, 3}], [{3, 4, 5}]))

        # Requirements abstracted to strings instead of types, overlap in "fizz"
        self.assertTrue(mapper.types_matching_data_requirements([{"foo", "bar", "fizz"}], [{"fizz", "buzz", "42"}]))

        # Requirements simplified to numbers instead of types, overlap in {2,3} in each one
        self.assertTrue(
            mapper.types_matching_data_requirements([{1, 2, 3}, {1, 2, 3}, {1, 2, 3}], [{2, 3}, {2, 3}, {2, 3}]))

        # Requirements simplified to numbers instead of types, no overlap in third element
        self.assertFalse(
            mapper.types_matching_data_requirements([{1, 2, 3}, {1, 2, 3}, {1, 2, 3}], [{2, 3}, {2, 3}, {42}]))

        # Requirements simplified to numbers instead of types, not enough elements to satisfy requirements
        self.assertFalse(mapper.types_matching_data_requirements([{1, 2, 3}], [{1, 2, 3}, {2, 3}]))

        # Requirements simplified to numbers instead of types, more elements than requirements
        self.assertFalse(mapper.types_matching_data_requirements([{1, 2, 3}, {1, 2, 3}], [{1, 2, 3}]))

    def test_is_multiple_data_consistent(self):
        #Simple control cases, intended behaviour
        self.assertTrue(
            mapper.is_multiple_data_consistent([{"number"}, {"text"}, {"text"}], 2))
        self.assertTrue(
            mapper.is_multiple_data_consistent([{"number"}, {"text"}, {"text"},{"text"}], 2))

        #Simple control case checking for offset
        self.assertTrue(
            mapper.is_multiple_data_consistent([{"number"}, {"date"}, {"text"}, {"text"}], 3))

        #All data elements can be interpreted as text, data is consistent
        self.assertTrue(
            mapper.is_multiple_data_consistent([{"number"}, {"text"}, {"date", "text"}, {"number", "text"}], 2))

        #Simple negative control case
        self.assertFalse(
            mapper.is_multiple_data_consistent([{"number"}, {"text"}, {"number"}], 2))

        #All data elements match one of the types of the reference element, but none with each other, making them inconsisten
        self.assertFalse(
            mapper.is_multiple_data_consistent([{"number"}, {"text","date"}, {"date"}, {"text"}], 2))

        #TODO: Expected behaviour for 0 and out-of-bounds lastelement-offset? Exception?
