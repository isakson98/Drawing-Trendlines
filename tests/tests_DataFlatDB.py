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


from DataBase.DataFlatDB import DataFlatDB

class Test_DataFlatDB(unittest.TestCase):

    def test_wrong_path(self):
        dir_top_down = ["data", "raw", "price"]
        good_obj = DataFlatDB(dir_top_down)
        
        dir_top_down = ["data", "dummy_data_1", "dummy_data_layer2"]
        bad_path = os.path.join(parent_dir_path, *dir_top_down)

        with self.assertRaises(ValueError) as cm:
            good_obj.change_dir(dir_top_down)

        failed_msg = f'{bad_path} does not exist! Reexamine the path'
        the_exception = cm.exception
        self.assertEqual(str(the_exception), failed_msg)

    # changes if the directory structure changes
    def test_suffix(self):
        dir_top_down = ["data", "raw", "price", "1_week"]
        good_obj = DataFlatDB(dir_top_down)
        self.assertEqual(good_obj.suffix, "_price_1_week.csv")

    def test_adding_retrieving_deleting(self):
        dir_top_down = ["data", "raw", "price", "1_week"]
        file_to_add = "add_dummy_file"
        sample_df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))

        # specify which directory you'll be working on 
        good_obj = DataFlatDB(dir_top_down)
        # only give root of what you are adding + suffix will be added automatically
        good_obj.add_data(file_to_add, sample_df)

        full_file_name = file_to_add + "_price_1_week.csv"
        pulled_data = good_obj.retrieve_data(full_file_name)
        duplicates_df = pd.concat([sample_df,pulled_data]).drop_duplicates(keep=False)
        self.assertEqual(len(duplicates_df), 0)

        file_removed = good_obj.remove(full_file_name)
        self.assertTrue(file_removed)


if __name__ == '__main__':
    unittest.main()