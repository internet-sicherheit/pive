import unittest

from traceback import print_exc

from multiprocessing import Process

from pive import inputmanager

class TestInputmanager(unittest.TestCase):

    def setUp(self):
        self.inputmanager = inputmanager.InputManager()

    def test_read_inconsistent_files(self):
        #Correctly formatted empty JSON-List
        try:
            self.inputmanager.read("./testcases/assets/empty1.json")
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

        # Correctly formatted JSON-List with empty object
        try:
            self.inputmanager.read("./testcases/assets/empty2.json")
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NOT_CONSISTENT_ERR_MSG)

        # Completely empty file
        try:
            self.inputmanager.read("./testcases/assets/empty3.json")
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

        # Regular text, not formatted
        try:
            self.inputmanager.read("./testcases/assets/nonsense.txt")
            self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

        #Large Nonsense file, random Base64 encoded data, expecting fast response
        def large_nonsense():
            try:
                self.inputmanager.read("./testcases/assets/big_nonsense.txt")
            except ValueError as e:
                self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

        p = Process(target=large_nonsense)
        p.start()
        p.join(timeout=5)
        if p.is_alive():
            p.terminate()
            self.fail("Timeout reached, still processing")
        else:
            self.assertEqual(p.exitcode, 0)



        # Data point with null-value
        try:
            self.inputmanager.read("./testcases/assets/inconsistent.json")
            self.fail(msg="Inconsistent data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NOT_CONSISTENT_ERR_MSG)


    def test_read_inconsistent_data(self):
        # same as test_read_inconsistent_files, but the content is passed instead of the path
        try:
            with open("./testcases/assets/empty1.json", "r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

        try:
            with open("./testcases/assets/empty2.json", "r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NOT_CONSISTENT_ERR_MSG)

        try:
            with open("./testcases/assets/empty3.json", "r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

        try:
            with open("./testcases/assets/nonsense.txt", "r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="No data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

            # Large Nonsense file, random Base64 encoded data, expecting fast response
            def large_nonsense():
                try:
                    with open("./testcases/assets/big_nonsense.txt", "r") as file:
                        self.inputmanager.read(file.read())
                except ValueError as e:
                    self.assertEqual(e.args[0], inputmanager.NO_DATA_LOADED_ERR_MSG)

            p = Process(target=large_nonsense)
            p.start()
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
                self.fail("Timeout reached, still processing")
            else:
                self.assertEqual(p.exitcode, 0)

        try:
            with open("./testcases/assets/inconsistent.json", "r") as file:
                self.inputmanager.read(file.read())
                self.fail(msg="Inconsistent data excepted")
        except ValueError as e:
            self.assertEqual(e.args[0], inputmanager.NOT_CONSISTENT_ERR_MSG)


    def test_read_consistent_files(self):

        # Known good files
        try:
            self.inputmanager.read("./samples/data/metadata/groupdata.json")
            self.inputmanager.read("./samples/data/metadata/numerical.json")
            self.inputmanager.read("./samples/data/metadata/simple_series.json")
            self.inputmanager.read("./samples/data/kv-list/groupdata.json")
            self.inputmanager.read("./samples/data/kv-list/numerical.json")
            self.inputmanager.read("./samples/data/kv-list/simple_series.json")
            self.inputmanager.read("./samples/data/simple-list/groupdata.json")
            self.inputmanager.read("./samples/data/simple-list/numerical.json")
            self.inputmanager.read("./samples/data/simple-list/simple_series.json")
            self.inputmanager.read("./samples/data/csv/groupdata.csv")
            self.inputmanager.read("./samples/data/csv/numerical.csv")
            self.inputmanager.read("./samples/data/csv/simple_series.csv")
        except Exception:
            self.fail("No error should occur during parsing of example files")

    def test_read_consistent_data(self):

        # same as test_read_consistent_files, but the content is passed instead of the path
        try:
            with open("./samples/data/metadata/groupdata.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/metadata/numerical.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/metadata/simple_series.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/kv-list/groupdata.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/kv-list/numerical.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/kv-list/simple_series.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/simple-list/groupdata.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/simple-list/numerical.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/simple-list/simple_series.json","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/csv/groupdata.csv","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/csv/numerical.csv","r") as file:
                self.inputmanager.read(file.read())

            with open("./samples/data/csv/simple_series.csv","r") as file:
                self.inputmanager.read(file.read())
        except Exception as e:
            self.fail(e)

    def test_mapping(self):

        # Check if expected chart types are chart types for sample data are still available
        #TODO: Add checks against new chart types here
        try:
            dataset = self.inputmanager.read("./samples/data/metadata/groupdata.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read("./samples/data/metadata/numerical.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read("./samples/data/metadata/simple_series.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

            dataset = self.inputmanager.read("./samples/data/kv-list/groupdata.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read("./samples/data/kv-list/numerical.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read("./samples/data/kv-list/simple_series.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

            dataset = self.inputmanager.read("./samples/data/simple-list/groupdata.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read("./samples/data/simple-list/numerical.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read("./samples/data/simple-list/simple_series.json")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

            dataset = self.inputmanager.read("./samples/data/csv/groupdata.csv")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("chordchart", suitables)

            dataset = self.inputmanager.read("./samples/data/csv/numerical.csv")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("scatterchart", suitables)
            self.assertIn("bubblechart", suitables)
            self.assertIn("linechart", suitables)

            dataset = self.inputmanager.read("./samples/data/csv/simple_series.csv")
            suitables = self.inputmanager.map(dataset)
            self.assertIn("piechart", suitables)
            self.assertIn("barchart", suitables)

        except Exception as e:
            print_exc()
            self.fail(e)