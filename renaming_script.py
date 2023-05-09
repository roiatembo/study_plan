import os, cv2, math
file_type = input("Which file type would you like to rename: ")
basepath = input("Enter full file path: ")
naming_type = input("What naming type is used, enter 's' for single or 'd' for double: ")

def list_files(basepath, file_type, naming_type = "s"):
    # List all subdirectories using os.listdir
    if naming_type == "s":
        pre = "0"
    else:
        pre = "00"

    list_dir = sorted(os.listdir(basepath))
    for folder in list_dir:
        print(folder)
        if os.path.isdir(os.path.join(basepath, folder)):
            full_path = basepath + "/" + folder
            for file_name in sorted(os.listdir(full_path)):
                if file_name.endswith(file_type):
                    split_name = file_name.split("-")[0]

                    if len(split_name) == 2:
                        os.rename(f"{full_path}/{file_name}", f"{full_path}/{pre}{file_name}")
                        

try:
    list_files(basepath, file_type, naming_type)
    print("Renaming successful")
except:
    print(f"Something went wrong, here is the issue")