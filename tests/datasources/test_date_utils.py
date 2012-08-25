
import unittest

from csxj.datasources.common.utils import is_date_in_range

class DateManipulationTestCases(unittest.TestCase):
    def setUp(self):
        self.date_range = "2012-01-01","2012-01-31"


    def test_in_range(self):
        self.assertTrue(is_date_in_range("2012-01-10", self.date_range))


    def test_out_of_range(self):
        self.assertFalse(is_date_in_range("2012-02-10", self.date_range))


    def test_is_start_date(self):
        self.assertTrue(is_date_in_range(self.date_range[0], self.date_range))


    def test_is_end_date(self):
        self.assertTrue(is_date_in_range(self.date_range[1], self.date_range))

