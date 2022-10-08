import os, cv2, math
from datetime import datetime, timedelta
video_dict = {}

def list_files(basepath, skipped_modules):
    # List all subdirectories using os.listdir
    list_dir = sorted(os.listdir(basepath))
    for folder in list_dir:
        if os.path.isdir(os.path.join(basepath, folder)):
            # check if they are any folders to skip
            if list_dir.index(folder) > skipped_modules:
                # list all mp4 files in selected folder

                full_path = basepath + "/" + folder
                for file_name in sorted(os.listdir(full_path)):
                    if file_name.endswith('.mp4'):
                        data = cv2.VideoCapture(full_path + "/" + file_name)
                        # count the number of frames
                        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
                        fps = data.get(cv2.CAP_PROP_FPS)

                        # calculate duration of the video
                        duration = round(frames / fps)
                        video_dict[file_name] = duration

    return video_dict

def write_to_file(study_txt, study_list, current_length, day_num, formatted_date, directory):
    study_txt = open(directory + "/Study_plan.txt", "a")
    minutes = str(math.floor(current_length / 60))
    study_txt.write("\nDay " + str(day_num) + "\n")
    study_txt.write(formatted_date + "\n")
    study_txt.write(f"Todays study videos consists of approximately {minutes} minutes\n")

    for vid in study_list:
        study_txt.write(vid + "\n")
    study_txt.close()

def study_plan(videos, length, duration_choice, start_date, directory):
    total_video_length = 0
    current_length = 0
    study_list = []
    day_num = 1

    # create a datetime object from passed start date string
    date_time_obj = datetime.strptime(start_date, '%Y-%m-%d')

    for v in videos:
        total_video_length += videos[v]

    if duration_choice == "d":
        # first checks if the entered value is end date or just days
        if type(length) is str:
            # create a datetime object from the passed end date string
            end_date_obj = datetime.strptime(length, '%Y-%m-%d')
            diff_days = end_date_obj - date_time_obj
            length = int(str(diff_days).split()[0]) #gets the total number of days and turns it into integer

        length_in_seconds = math.floor(total_video_length / length)
        days = length
    else:
        length_in_seconds = length * 60
        days = math.floor(total_video_length / length_in_seconds)

    study_time = length_in_seconds
    minutes_per_day = str(math.floor(length_in_seconds/60))
    study_txt = open(directory + "/Study_plan.txt", "w")
    study_txt.write("Your study plan consists of approximately " + minutes_per_day + " minutes for " + str(days) + " days\n")
    study_txt.close()

    for v in videos:
        if length_in_seconds > 0:
            study_list.append(v)
            length_in_seconds -= videos[v]
            current_length += videos[v]
        else:
            # record into text file
            formatted_date = date_time_obj.strftime("%A %d %B %Y")
            write_to_file(study_txt, study_list, current_length, day_num, formatted_date, directory)

            # start over
            date_time_obj = date_time_obj + timedelta(days=1)
            day_num += 1
            current_length = 0
            study_list = []
            study_list.append(v)
            length_in_seconds = study_time

    # add the last videos to file
    if len(study_list) > 0:
        write_to_file(study_txt, study_list, current_length, day_num, formatted_date, directory)
