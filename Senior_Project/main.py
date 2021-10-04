'''

if new type of data arrives -> manually create a folder or reorganize stuff
then give the location to DataReceiveExtractor class

need some kind of structure that verifies the data directories


THIS OF THIS AS A CLIENT SPACE.
This is the researcher ground.
This is where you are going to request and write stuff and ask for analysis
Do not delegate everything to library classes, as this overfits stuff (no hard coding)


'''
# popular scripts, combination of all modules features above
from CommonScripts import CommonScripts
from DataBase.popular_paths import popular_paths

# robot made
import time


if __name__ == '__main__':
    start = time.time()
    ###################################################################
    # PLACE SCRIPT BETWEEN THE TWO LINES
    ###################################################################
    comm_obj = CommonScripts()
    comm_obj.concat_all_directory_files(popular_paths['bull triangles 1 day']["dir_list"], 
                                        popular_paths['big data']["dir_list"], 
                                        "big_bull_triangles")
    ##################################################################
    end = time.time()
    print(str(end-start) + " seconds")