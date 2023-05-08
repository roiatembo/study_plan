import os, cv2, math
# file_type = input("Which file type would you like to rename: ")


def list_files(basepath, file_type, skipped_modules = 0):
    # List all subdirectories using os.listdir
    list_dir = sorted(os.listdir(basepath))
    for folder in list_dir:
        if os.path.isdir(os.path.join(basepath, folder)):
            # check if they are any folders to skip
            if list_dir.index(folder) > skipped_modules:
                # list all mp4 files in selected folder

                full_path = basepath + "/" + folder
                for file_name in sorted(os.listdir(full_path)):
                    if file_name.endswith(file_type):
                        split_name = file_name.split("-")[0]
                        print(file_name)
                        print(len(split_name))
                        

    # return split_name

list_files("/home/roia/Videos/Tutorials/data_science", "mp4")