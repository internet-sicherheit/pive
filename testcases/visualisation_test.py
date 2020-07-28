import unittest

from traceback import print_exc

import pive.environment as environment
import pive.inputmanager as inputmanager

import os
import shutil

class TestInputmanager(unittest.TestCase):

    #Simple test cases to check if something broke basic functionality

    def setUp(self):
        self.manager = inputmanager.InputManager(mergedata=False)
        self.env = environment.Environment(inputmanager=self.manager, outputpath=self.output_path())

    def tearDown(self):
        self.manager = None
        self.env = None
        shutil.rmtree(self.output_path(), ignore_errors=True)

    def output_path(self):
        if os.name == 'nt':
            return os.path.join(os.environ["TEMP"], "\\ivod-testing")
        else:
            return "/tmp/ivod-testing"


    def test_chord_chart_generation(self):
        try:
            supported = self.env.load("./samples/data/metadata/groupdata.json")
            self.assertIn(environment.CHART_CHORD, supported)
            chart = self.env.choose(environment.CHART_CHORD)
            self.env.render(chart)
        except Exception as e:
            self.fail(str(e))


    def test_scatter_chart_generation(self):
        try:
            supported = self.env.load("./samples/data/metadata/numerical.json")
            self.assertIn(environment.CHART_SCATTER, supported)
            chart = self.env.choose(environment.CHART_SCATTER)
            self.env.render(chart)
        except Exception as e:
            self.fail(str(e))

    def test_bubble_chart_generation(self):
        try:
            supported = self.env.load("./samples/data/metadata/numerical.json")
            self.assertIn(environment.CHART_BUBBLE, supported)
            chart = self.env.choose(environment.CHART_BUBBLE)
            self.env.render(chart)
        except Exception as e:
            self.fail(str(e))

    def test_line_chart_generation(self):
        try:
            supported = self.env.load("./samples/data/metadata/numerical.json")
            self.assertIn(environment.CHART_LINE, supported)
            chart = self.env.choose(environment.CHART_LINE)
            self.env.render(chart)
        except Exception as e:
            self.fail(str(e))

    def test_pie_chart_generation(self):
        try:
            supported = self.env.load("./samples/data/metadata/simple_series.json")
            self.assertIn(environment.CHART_PIE, supported)
            chart = self.env.choose(environment.CHART_PIE)
            self.env.render(chart)
        except Exception as e:
            self.fail(str(e))

    def test_bar_chart_generation(self):
        try:
            supported = self.env.load("./samples/data/metadata/simple_series.json")
            self.assertIn(environment.CHART_BAR, supported)
            chart = self.env.choose(environment.CHART_BAR)
            self.env.render(chart)
        except Exception as e:
            self.fail(str(e))

    #TODO: Check if generated code or rendered code matches expectations (How to determine that? Behaviour? Image comparison?)