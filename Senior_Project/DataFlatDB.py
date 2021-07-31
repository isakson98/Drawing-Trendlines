import os
import datetime as dt
import pandas as pd
from pandas.core.frame import DataFrame


'''
This class is solely responsible for dealing with files in my database.
Each database has 4 essential functions:
- add
- update
- remove
- retrieve

In essense, this class deals exactly with that. Specify the directory you want
to work in at the start or change it if you have to, and all you have to do then


The beauty of this approach is that it is very flexible. You can rearrange/add
folders if you find this necessary without any additional changes to the code
in this class. This works because the burden of identifying which folder you 
want to work with lies on you. That's fine, because this project is built as
a researcher playground, and as a researcher using these classes you have 
common sense to supply info in a correct fashion. There are several exceptions,
and if statements that protect user in some ways from messing up

PS. can think of this as a wrapper for the os module
'''
class DataFlatDB:

    root_data_dir = os.path.dirname(__file__)
    dir_operated_on = None

    '''
    params:
        dir_list_to_operate_in -> list of top-down directories that lead to the one you want to work on

    it is intended to use an object of this class to operate on one directory
    at a time. Use two of these objects if you have simultenous tasks. 
    '''
    def __init__(self, dir_list_to_operate_in : list):
        self.change_dir(dir_list_to_operate_in)

    ###################
    # Private Methods #
    ###################

    '''
    params:
        list_dir -> list of directories in top-down order for concatenation

    helper function used in all functions available to the user of this class
    this function concatonates the given elements in the list 

    returns:
        string_path -> the full path given 
    '''
    def __merge_path_content(self, list_dir : list) -> str:
        # asterisk before list expands list into number of elements it has
        string_path = os.path.join(self.root_data_dir, *list_dir)

        # string_path = self.root_data_dir
        # for dir in list_dir:
        #     string_path = os.path.join(string_path, dir)

        return string_path

    '''
    params:
        string_path -> the path given to verify

    this function is used before operating on existing files
    to verify that the file actually exists

    returns:
        boolean -> True if file exists / False otherwise
    '''
    def __verify_path_existence(self, string_path : str):

        if not os.path.exists(string_path):
            raise ValueError(f'{string_path} does not exist! Reexamine the path')

    '''
    params
        file_path -> path to file to be renamed

    this function is used when a new version of data is available,
    but the old one is decided to be saved as well. Use this function
    to add date to the outdated file, so as to show that it is an old file

    returns:
        new_path_old_file -> new path of the old file, the one renamed
    '''
    def __add_date_to_file_name(self, file_path : str) -> str:
        directory, file_name =  os.path.split(file_path)
        _, str_date = self.__get_files_creation_date(file_path)
        new_file_name = str_date + "_" + file_name 
        new_path_old_file = os.path.join(directory, new_file_name)
        
        if os.path.exists(new_path_old_file) == False:
            os.rename(file_path, new_path_old_file)

        return new_path_old_file

    '''
    params:
        path -> path of the file

    helper function that fetches the creation date of the file

    returns 
        creation_date -> datetime object of the date
        string_v -> string version of the date for adding to file name
    '''
    def __get_files_creation_date(self, path : str) -> list:

        timestamp_creation = os.stat(path).st_ctime
        creation_date = dt.datetime.fromtimestamp(timestamp_creation)
        string_v = creation_date.strftime("%d-%b-%Y")
        return [creation_date, string_v]

    ##################
    # Public Methods #
    ##################

    '''
    params:
        name_of_file -> name of the file to be added
        content_to_add -> content of this new file

    one of core functions of this class. use this function to create new files
    '''
    def add_data(self, name_of_file : str, content_to_add : pd.DataFrame):
        full_path = self.__merge_path_content([self.dir_operated_on, name_of_file])
        content_to_add.to_csv(full_path, index=False)

    '''
    params:
        name_of_file -> name of the file to be added
        content_to_add -> content of this new file
        keep_old -> boolean, if yes, existing old data will be kept but renamed, with date added
    '''
    def update_data(self, name_of_file, content_to_add, keep_old):
        full_path = self.__merge_path_content([self.dir_operated_on, name_of_file])
        if keep_old:
            self.__add_date_to_file_name(full_path)

    '''
    params:
        name_of_file -> name of file you want data of

    if no files is given, you return everything containing in that folder

    TODO: think of using processes to split up the work, use a generator/yield as a client
    '''
    def retrieve_all(self) -> pd.DataFrame():
        big_list = list()
        for file_name in os.listdir(self.dir_operated_on):
            big_list.append(self.retrieve(file_name))
        return big_list

    '''
    params:
        name_of_file -> name of file you want data of

    if no files is given, you return everything containing in that folder

    TODO: think of using processes to split up the work, use a generator/yield as a client
    '''
    def retrieve(self, name_of_file="") -> pd.DataFrame():
        full_path = self.__merge_path_content(self.dir_operated_on, name_of_file)
        return pd.read_csv(full_path)

    '''
    params:
        name_of_file -> name of file you want data of

    this function deletes a file (if that ever becomes necessary)
    '''
    def remove(self, name_of_file):
        full_path = self.__merge_path_content(self.dir_operated_on, name_of_file)
        os.remove(full_path)

    '''
    params:
        dir_list_to_operate_in -> list of top-down directories that lead to the one you want to work on

    I am anticipating working a lot with a lot of files just one directory at a time.
    To avoid overhead constantly verifying full file path for every file, 
    I decided to allow to specify it just once. This way it's not done redundantly.
    If you decide to change the directory, you can do it using this function.
    It will change the member variable that is used in all main functions,
    that stores the full path to the directory 

    returns:
        str_dir -> full path given as a list as a param turned into a string
    '''
    def change_dir(self, dir_list_to_operate_in : list):
        str_dir = self.__merge_path_content(dir_list_to_operate_in)
        self.__verify_path_existence(str_dir)
        self.dir_operated_on = str_dir
        return str_dir


    '''
    params:
        file_name -> name of the file to have an operation on

    helper function that verifies that the name of the file matches
    the directory it is in and parent directory of the directory it is in.

    if price/1_day/file_name, file_name must have price_1_day as suffix of the name

    '''
    def create_filename_standard(self, file_name, ext="csv"):

        return True

