import unittest

from traceback import print_exc

from pive.datavalidater import count_keys_in_raw_data, get_all_keys_in_dataset, determine_shared_keys_in_dataset, \
    generate_valid_dataset_from_shared_keys, generate_valid_dataset, validate_data_keys

from collections import OrderedDict


class TestDataValidater(unittest.TestCase):

    def test_count_keys_in_raw_data(self):

        # Simple Test Cases
        self.assertEqual(count_keys_in_raw_data([OrderedDict([("x", 1), ("y", 2)]) ]), OrderedDict({("x", "y"): 1}))
        self.assertEqual(count_keys_in_raw_data([OrderedDict([("x", 1), ("y", 2)]), OrderedDict([("a", 1), ("b", 2)])]), OrderedDict([(('x', 'y'), 1), (('a', 'b'), 1)]))

        # No input data
        self.assertEqual(count_keys_in_raw_data([]), OrderedDict())

        # Empty input data
        self.assertEqual(count_keys_in_raw_data([OrderedDict()]), OrderedDict())
        self.assertEqual(count_keys_in_raw_data([OrderedDict(), OrderedDict()]), OrderedDict())

        # Simple case with mixed order
        self.assertEqual(count_keys_in_raw_data([OrderedDict([("x", 1), ("y", 2)]), OrderedDict([("y", 1), ("x", 2) ] ) ]), OrderedDict([(('x', 'y'), 1), (('y', 'x'), 1)]))

    def test_validate_data_keys(self):

        # Test empty data
        data = OrderedDict()
        self.assertEqual(validate_data_keys(data), [])

        # Test simple data
        data = OrderedDict({("x", "y"): 2})
        self.assertEqual(validate_data_keys(data), ["x", "y"])

        #TODO: Check for wrong and nonsense inputs

        # Test invalid data
        try:
            data = OrderedDict({("x", "y"): -1})
            validate_data_keys(data)
            self.fail("Invalid input not handled")
        except Exception:
            pass

        try:
            data = OrderedDict({("x", "y"): None})
            validate_data_keys(data)
            self.fail("Invalid input not handled")
        except Exception:
            pass

        try:
            data = OrderedDict([(("x", "y"), -1), ("z", 2)])
            validate_data_keys(data)
            self.fail("Invalid input not handled")
        except Exception:
            pass


        # Test order on equal count
        data = OrderedDict([(("x", "y"), 2), ("z", 2)])
        self.assertEqual(validate_data_keys(data), ["z"])

        #Test key that is subset of another key
        data = OrderedDict([(("x", "y"), 2), ("x", 2)])
        self.assertEqual(validate_data_keys(data), ["x"])

    def test_generate_valid_dataset(self):

        # Simple test
        data = [OrderedDict([("x", 1), ("y", 2)]), OrderedDict([("x", 3), ("y", 4)]) ]
        self.assertEqual(generate_valid_dataset(validate_data_keys(count_keys_in_raw_data(data)), data), data)

        # No data
        data = []
        self.assertEqual(generate_valid_dataset(validate_data_keys(count_keys_in_raw_data(data)), data), [])

        data = [OrderedDict()]
        self.assertEqual(generate_valid_dataset(validate_data_keys(count_keys_in_raw_data(data)), data), [OrderedDict()])

        # Data with mixed up order but same keys
        data = [OrderedDict([("x", 1), ("y", 2)]),OrderedDict([("y", 4),("x", 3)])]
        self.assertEqual(generate_valid_dataset(validate_data_keys(count_keys_in_raw_data(data)), data),
                         [OrderedDict([("y", 4),("x", 3)])])


    def test_get_all_keys_in_dataset(self):
        # Single element
        self.assertEqual(set(get_all_keys_in_dataset([OrderedDict({"x": 1, "y": 2})])), {"x", "y"})

        # disjoint data
        self.assertEqual(set(get_all_keys_in_dataset([OrderedDict({"x": 1, "y": 2}), OrderedDict({"a": 1, "b": 2})])), {"a", "b", "x", "y"})

        # partially disjoint data
        self.assertEqual(set(get_all_keys_in_dataset([OrderedDict({"x": 1, "y": 2}), OrderedDict({"x": 1, "b": 2})])), {"b", "x", "y"})

        # no data
        self.assertEqual(get_all_keys_in_dataset([]), [])

    def test_determine_shared_keys_in_dataset(self):

        # No overlap
        data = [OrderedDict({"x": 1, "y": 2}), OrderedDict({"a": 1, "b": 2})]
        self.assertEqual(determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), [])

        # partial overlap between all elements
        data = [OrderedDict({"x": 1, "y": 2}), OrderedDict({"x": 1, "b": 2})]
        self.assertEqual(determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), ["x"])

        # partial overlap between any 2 pairs, but no total overlap
        data = [OrderedDict({"x": 1, "y": 2}), OrderedDict({"y": 1, "z": 2}), OrderedDict({"x": 1, "z": 2})]
        self.assertEqual(determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), [])

        # partial overlap between all elements, with different numbers of sub-elements
        data = [OrderedDict({"x": 1, "y": 2, "z": 3}), OrderedDict({"y": 1, "z": 2}), OrderedDict({"x": 1, "z": 2})]
        self.assertEqual(determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), ["z"])

        # empty data
        data = [OrderedDict()]
        self.assertEqual(determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), [])

    def test_generate_valid_dataset_from_shared_keys(self):

        # partial overlap between all elements, with different numbers of sub-elements
        data = [OrderedDict({"x": 1, "y": 2, "z": 3}), OrderedDict({"y": 1, "z": 2}), OrderedDict({"x": 1, "z": 1})]
        self.assertEqual(generate_valid_dataset_from_shared_keys(
            determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), data),
            [{"z": 3}, {"z": 2}, {"z": 1}])

        data = [OrderedDict({"x": 1, "y": 1, "z": 3}), OrderedDict({"y": 1, "z": 2}), OrderedDict({"y": 1, "z": 1})]
        self.assertEqual(generate_valid_dataset_from_shared_keys(
            determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), data),
            [{"y": 1, "z": 3}, {"y": 1, "z": 2}, {"y": 1, "z": 1}])

        # empty data
        data = [OrderedDict()]
        self.assertEqual(generate_valid_dataset_from_shared_keys(
            determine_shared_keys_in_dataset(get_all_keys_in_dataset(data), data), data), [])
