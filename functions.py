import os, cv2, math
from datetime import datetime, timedelta
video_dict = {}

def list_files(basepath, skipped_modules):
    # List all subdirectories using os.listdir
    list_dir = sorted(os.listdir(basepath))
    for folder in list_dir:
        video_dict[folder] = []
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
                        video_dict[folder].append([file_name, duration])

    return video_dict

def write_to_file(study_txt, study_list, current_length, day_num, formatted_date, directory):
    study_txt = open(directory + "/Study_plan.txt", "a+")
    if day_num < 10:
        pre = "0"
    else:
        pre = ""

    playlist_file = open(f"{directory}/playlists/{pre}{str(day_num)}. {formatted_date}.m3u", "a+")
    minutes = str(math.floor(current_length / 60))
    study_txt.write("\nDay " + str(day_num) + "\n")
    study_txt.write(formatted_date + "\n")
    study_txt.write(f"Todays study videos consists of approximately {minutes} minutes\n")

    for vid in study_list:
        video_name = vid.split(";")[1]
        folder_name = vid.split(";")[0]
        study_txt.write(video_name + "\n")
        playlist_file.write(f"{directory}/{folder_name}/{video_name}\n")
    study_txt.close()






def study_plan(videos, length, duration_choice, start_date, directory, skip_days):
    total_video_length = 0
    current_length = 0
    study_list = []
    day_num = 1
    skipped_days = skip_days.split()

    # create a playlist folder if it doesn't exist
    try:
        os.mkdir(f"{directory}/playlists")
    except FileExistsError:
        # delete existing files
        files = os.listdir(f"{directory}/playlists")
        for playlist in files:
            os.remove(f"{directory}/playlists/{playlist}")


    # create a datetime object from passed start date string
    date_time_obj = datetime.strptime(start_date, '%Y-%m-%d')

    for list_vid in videos:
        if len(videos[list_vid]) > 0:
            for vid in videos[list_vid]:
                total_video_length += vid[1]

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
    study_txt.close()
  

    for list_vid in videos:
        if len(videos[list_vid]) > 0:
            for vid in videos[list_vid]:
                if length_in_seconds > 0:
                    study_list.append(f"{list_vid};{vid[0]}")
                    length_in_seconds -= vid[1]
                    current_length += vid[1]
                else:
                    # record into text file
                    formatted_date = date_time_obj.strftime("%A %d %B %Y")
                    if date_time_obj.strftime("%a").lower() in skipped_days:
                        date_time_obj = date_time_obj + timedelta(days=1)
                        continue
                    else:
                        write_to_file(study_txt, study_list, current_length, day_num, formatted_date, directory)

                        # start over
                        date_time_obj = date_time_obj + timedelta(days=1)
                        day_num += 1
                        current_length = 0
                        study_list = []
                        study_list.append(f"{list_vid};{vid[0]}")
                        length_in_seconds = study_time

    # add the last videos to file
    if len(study_list) > 0:
        formatted_date = date_time_obj.strftime("%A %d %B %Y")
        write_to_file(study_txt, study_list, current_length, day_num, formatted_date, directory)


    with open(directory + "/Study_plan.txt", 'r+') as f:
        content = f.read()
        line = "Your study plan consists of approximately " + minutes_per_day + " minutes for " + str(day_num) + " days"
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

