""" Module for testing the filter options window """
import sys
sys.path.append('visualization')
import unittest
from visualization.plot_utils import *
from preprocessing.edf_loader import EdfLoader

class TestPlotUtils(unittest.TestCase):
    def setUp(self):
        # Set the test files
        self.TEST_FN = "/Users/daniellecurrey/Desktop/gui_edf_files/chb01_03.edf"
        loader = EdfLoader()
        self.EDF_INFO = loader.load_metadata(self.TEST_FN)

    # 0. Check annotations
    def test_check_annotations(self):
        # Test check annotations
        self.EDF_INFO.annotations = np.array(self.EDF_INFO.annotations)
        ret, idx_w_ann = check_annotations(0, 10, self.EDF_INFO)
        self.assertEqual(len(ret), 2)
        self.assertEqual(len(idx_w_ann), 10)
        for x, y in zip(ret[0], self.EDF_INFO.annotations[:,0]):
            self.assertEqual(x, y)
        for x, y in zip(ret[1], self.EDF_INFO.annotations[:,1]):
            self.assertEqual(x, y)
        ret, idx_w_ann = check_annotations(532, 10, self.EDF_INFO)
        self.assertEqual(len(ret), 2)
        self.assertEqual(len(idx_w_ann), 10)
        for x, y in zip(ret[0], self.EDF_INFO.annotations[:,16]):
            self.assertEqual(x, y)
        for x, y in zip(ret[1], self.EDF_INFO.annotations[:,17]):
            self.assertEqual(x, y)
        test_edf = self.EDF_INFO
        test_edf.annotations = [[], [], []]
        ret, idx_w_ann = check_annotations(532, 10, test_edf)
        self.assertEqual(ret, [])
        self.assertEqual(len(idx_w_ann), 10)

        test_edf.annotations = np.array([[2, 3, 9], [-1, -1, -1], ["test2", "test3", "test9"]])
        ret, idx_w_ann = check_annotations(0, 10, test_edf)
        self.assertEqual(len(ret), 3)
        self.assertEqual(len(idx_w_ann), 10)
        for i in range(10):
            if i != 2 and i != 3:
                self.assertEqual(idx_w_ann[i], 0)
            else:
                self.assertEqual(idx_w_ann[i], 1)

        
    # 1. Filter data
    def test_filter_data(self):
        # TODO
        pass

    # 2. Convert from count
    def test_convert_from_count(self):
        # Test convert from count
        h, m, s = convert_from_count(0)
        self.assertEqual(h, 0)
        self.assertEqual(m, 0)
        self.assertEqual(s, 0)
        h, m, s = convert_from_count(72)
        self.assertEqual(h, 0)
        self.assertEqual(m, 1)
        self.assertEqual(s, 12)
        h, m, s = convert_from_count(3624)
        self.assertEqual(h, 1)
        self.assertEqual(m, 0)
        self.assertEqual(s, 24)
    
    # 3. Get time
    def test_get_time(self):
        # Test get time
        str0 = get_time(0)
        self.assertEqual(str0, "0:00:00")
        str0 = get_time(72)
        self.assertEqual(str0, "0:01:12")
        str0 = get_time(3624)
        self.assertEqual(str0, "1:00:24")
        str0 = get_time(759)
        self.assertEqual(str0, "0:12:39")


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)
