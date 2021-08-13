import sys
import unittest
import os
import pandas as pd
import numpy as np

# appending parent path, so Python knows where the source code it
parent_dir_path = os.path.dirname(__file__)
parent_dir_path = os.path.dirname(parent_dir_path)
parent_dir_path = os.path.join(parent_dir_path, "Senior_Project")
sys.path.append(parent_dir_path)


from DataBase.DataDownload import DataDownload

class Test_DataDownload(unittest.TestCase):
    '''
    testing if dwn_price_data() returns proper results if bad input
    '''
    def test_wrong_price_data_call(self):
        test_obj = DataDownload()
        data = test_obj.dwn_price_data('ticker', 1, 'day')
        content_len = len(data)
        self.assertEqual(content_len, 0)


if __name__ == '__main__':
    unittest.main()