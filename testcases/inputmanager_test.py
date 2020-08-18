import unittest

from traceback import print_exc

import multiprocessing as mp

from pive import inputmanager as im

from pathlib import Path
import pickle

class TestInputmanager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mp.set_start_method('spawn')

    def setUp(self):
        self.inputmanager = im.InputManager()

    def test_read_inconsistent_files(self):
        #Correctly formatted empty JSON-List
        try:
            self.inputmanager.read(Path("./testcases/assets/empty1.json"))
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NO_DATA_LOADED_ERR_MSG)

        # Correctly formatted JSON-List with empty object
        try:
            self.inputmanager.read(Path("./testcases/assets/empty2.json"))
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NOT_CONSISTENT_ERR_MSG)

        # Completely empty file
        try:
            self.inputmanager.read(Path("./testcases/assets/empty3.json"))
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NO_DATA_LOADED_ERR_MSG)

        # Regular text, not formatted
        try:
            self.inputmanager.read(Path("./testcases/assets/nonsense.txt"))
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NO_DATA_LOADED_ERR_MSG)

        p = mp.Process(target=large_nonsense_file, args=(self.inputmanager,))
        p.start()
        p.join(timeout=10)
        if p.is_alive():
            p.terminate()
            self.fail("Timeout reached, still processing")
        else:
            self.assertEqual(p.exitcode, 0)



        # Data point with null-value
        try:
            self.inputmanager.read(Path("./testcases/assets/inconsistent.json"))
            self.fail(msg="Inconsistent data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NOT_CONSISTENT_ERR_MSG)


    def test_read_inconsistent_data(self):
        # same as test_read_inconsistent_files, but the content is passed instead of the path
        try:
            with Path("./testcases/assets/empty1.json").open(mode="r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NO_DATA_LOADED_ERR_MSG)

        try:
            with Path("./testcases/assets/empty2.json").open(mode="r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NOT_CONSISTENT_ERR_MSG)

        try:
            with Path("./testcases/assets/empty3.json").open(mode="r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NO_DATA_LOADED_ERR_MSG)

        try:
            with Path("./testcases/assets/nonsense.txt").open(mode="r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NO_DATA_LOADED_ERR_MSG)

        p = mp.Process(target=large_nonsense_text, args=(self.inputmanager,))
        p.start()
        p.join(timeout=10)
        if p.is_alive():
            p.terminate()
            self.fail("Timeout reached, still processing")
        else:
            self.assertEqual(p.exitcode, 0)

        try:
            with Path("./testcases/assets/inconsistent.json").open(mode="r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="Inconsistent data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], im.NOT_CONSISTENT_ERR_MSG)


    def test_read_consistent_files(self):

        # Known good files
        try:
            self.inputmanager.read(Path("./samples/data/metadata/groupdata.json"))
            self.inputmanager.read(Path("./samples/data/metadata/numerical.json"))
            self.inputmanager.read(Path("./samples/data/metadata/simple_series.json"))
            self.inputmanager.read(Path("./samples/data/kv-list/groupdata.json"))
            self.inputmanager.read(Path("./samples/data/kv-list/numerical.json"))
            self.inputmanager.read(Path("./samples/data/kv-list/simple_series.json"))
            self.inputmanager.read(Path("./samples/data/simple-list/groupdata.json"))
            self.inputmanager.read(Path("./samples/data/simple-list/numerical.json"))
            self.inputmanager.read(Path("./samples/data/simple-list/simple_series.json"))
            self.inputmanager.read(Path("./samples/data/csv/groupdata.csv"))
            self.inputmanager.read(Path("./samples/data/csv/numerical.csv"))
            self.inputmanager.read(Path("./samples/data/csv/simple_series.csv"))
        except Exception:
            self.fail("No error should occur during parsing of example files")

    def test_read_consistent_data(self):

        # same as test_read_consistent_files, but the content is passed instead of the path
        try:
            with Path("./samples/data/metadata/groupdata.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/metadata/numerical.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/metadata/simple_series.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/kv-list/groupdata.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/kv-list/numerical.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/kv-list/simple_series.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/simple-list/groupdata.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/simple-list/numerical.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/simple-list/simple_series.json").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/csv/groupdata.csv").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/csv/numerical.csv").open(mode="r") as file:
                self.inputmanager.read(file.read())

            with Path("./samples/data/csv/simple_series.csv").open(mode="r") as file:
                self.inputmanager.read(file.read())
        except Exception as e:
            self.fail(e)

    def test_mapping(self):

        # Check if expected chart types are chart types for sample data are still available
        #TODO: Add checks against new chart types here
        try:
            dataset = self.inputmanager.read(Path("./samples/data/metadata/groupdata.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/metadata/numerical.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/metadata/simple_series.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/kv-list/groupdata.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/kv-list/numerical.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/kv-list/simple_series.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/simple-list/groupdata.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/simple-list/numerical.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/simple-list/simple_series.json"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/csv/groupdata.csv"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/csv/numerical.csv"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read(Path("./samples/data/csv/simple_series.csv"))
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

        except Exception as e:
            print_exc()
            self.fail(e)

# Large Nonsense file, random Base64 encoded data, expecting fast response
def large_nonsense_text(inputmanager):
    try:
        with Path("./testcases/assets/big_nonsense.txt").open(mode="r") as file:
            inputmanager.read(file.read())
    except ValueError as e:
        assert e.args[0] == im.NO_DATA_LOADED_ERR_MSG

#Large Nonsense file, random Base64 encoded data, expecting fast response
def large_nonsense_file(inputmanager):
    try:
        inputmanager.read(Path("./testcases/assets/big_nonsense.txt"))
    except ValueError as e:
        assert e.args[0] == im.NO_DATA_LOADED_ERR_MSG