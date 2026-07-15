import os
import json
import math
import cv2
from datetime import datetime, timedelta

# Extensions we'll treat as "video" files when scanning a course folder.
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.mov', '.avi', '.webm', '.m4v')
CACHE_FILENAME = ".duration_cache.json"


def _load_cache(basepath):
    """Load the duration cache for a course directory, if it exists."""
    cache_path = os.path.join(basepath, CACHE_FILENAME)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(basepath, cache):
    """Persist the duration cache so re-scans of the same course are fast."""
    cache_path = os.path.join(basepath, CACHE_FILENAME)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except OSError:
        # Caching is a nice-to-have; never fail the scan because of it.
        pass


def _get_video_duration(full_file_path):
    """
    Return the duration (in whole seconds) of a video file, or None if the
    file can't be read / has no valid frame rate. Always releases the
    VideoCapture handle.
    """
    data = cv2.VideoCapture(full_file_path)
    try:
        if not data.isOpened():
            return None
        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = data.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0 or not frames or frames <= 0:
            return None
        return round(frames / fps)
    finally:
        data.release()


def list_files(basepath, skipped_modules, use_cache=True, show_progress=True):
    """
    Scan `basepath` for module subfolders and the video files inside them,
    returning {folder_name: [[file_name, duration_seconds], ...]}.

    - skipped_modules: number of leading module folders (by sorted order) to
      skip entirely.
    - use_cache: read/write a per-course cache keyed on filename+size+mtime
      so re-scanning an already-processed course doesn't re-read every file.
    - show_progress: print a lightweight progress indicator while scanning.
    """
    if not os.path.isdir(basepath):
        raise FileNotFoundError(f"Course directory not found: {basepath}")

    video_dict = {}
    cache = _load_cache(basepath) if use_cache else {}
    skipped_files = []

    list_dir = sorted(os.listdir(basepath))
    module_folders = [f for f in list_dir if os.path.isdir(os.path.join(basepath, f))]

    for index, folder in enumerate(module_folders):
        if index < skipped_modules:
            continue

        video_dict[folder] = []
        full_path = os.path.join(basepath, folder)
        video_files = sorted(
            f for f in os.listdir(full_path) if f.lower().endswith(VIDEO_EXTENSIONS)
        )

        for file_name in video_files:
            file_path = os.path.join(full_path, file_name)
            try:
                stat = os.stat(file_path)
            except OSError:
                skipped_files.append(file_name)
                continue

            cache_key = f"{folder}/{file_name}"
            cached = cache.get(cache_key)
            fingerprint = [stat.st_size, stat.st_mtime]

            if cached and cached.get("fingerprint") == fingerprint:
                duration = cached["duration"]
            else:
                duration = _get_video_duration(file_path)
                if duration is None:
                    skipped_files.append(file_name)
                    continue
                cache[cache_key] = {"fingerprint": fingerprint, "duration": duration}

            video_dict[folder].append([file_name, duration])

            if show_progress:
                print(f"Scanned: {folder}/{file_name} ({duration}s)")

    if use_cache:
        _save_cache(basepath, cache)

    if skipped_files:
        print(
            f"\nWarning: {len(skipped_files)} file(s) could not be read and were "
            f"skipped (corrupted or unsupported):"
        )
        for name in skipped_files:
            print(f"  - {name}")

    return video_dict


def write_to_file(study_list, current_length, day_num, formatted_date, directory, day_width):
    """Append one day's entry to Study_plan.txt and write its .m3u playlist."""
    day_label = str(day_num).zfill(day_width)
    minutes = math.floor(current_length / 60)

    with open(os.path.join(directory, "Study_plan.txt"), "a", encoding="utf-8") as study_txt:
        study_txt.write(f"\nDay {day_num}\n")
        study_txt.write(formatted_date + "\n")
        study_txt.write(f"Todays study videos consists of approximately {minutes} minutes\n")
        for vid in study_list:
            folder_name, video_name = vid.split(";", 1)
            study_txt.write(video_name + "\n")

    playlist_path = os.path.join(directory, "playlists", f"{day_label}. {formatted_date}.m3u")
    with open(playlist_path, "a", encoding="utf-8") as playlist_file:
        for vid in study_list:
            folder_name, video_name = vid.split(";", 1)
            playlist_file.write(f"{directory}/{folder_name}/{video_name}\n")


def study_plan(videos, length, duration_choice, start_date, directory, skip_days):
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Course directory not found: {directory}")

    total_video_length = 0
    current_length = 0
    study_list = []
    day_num = 1
    skipped_days = skip_days.split()

    # Create (or clean out) the playlists folder.
    playlists_dir = os.path.join(directory, "playlists")
    os.makedirs(playlists_dir, exist_ok=True)
    for playlist in os.listdir(playlists_dir):
        os.remove(os.path.join(playlists_dir, playlist))

    date_time_obj = datetime.strptime(start_date, '%Y-%m-%d')

    for list_vid in videos:
        for vid in videos[list_vid]:
            total_video_length += vid[1]

    if total_video_length == 0:
        raise ValueError(
            "No usable video files were found, so a study plan can't be generated. "
            "Check the course directory and the number of skipped modules."
        )

    if duration_choice == "d":
        if isinstance(length, str):
            end_date_obj = datetime.strptime(length, '%Y-%m-%d')
            length = (end_date_obj - date_time_obj).days
        if length <= 0:
            raise ValueError("The number of study days must be greater than zero.")

        length_in_seconds = math.floor(total_video_length / length)
        days = length
    else:
        length_in_seconds = length * 60
        if length_in_seconds <= 0:
            raise ValueError("Minutes per day must be greater than zero.")
        days = max(1, math.floor(total_video_length / length_in_seconds))

    if length_in_seconds <= 0:
        raise ValueError(
            "The study period is too long for the amount of video available "
            "(each day would get 0 seconds of content)."
        )

    study_time = length_in_seconds
    minutes_per_day = math.floor(length_in_seconds / 60)
    # Zero-pad day numbers wide enough for the expected total number of days
    # (minimum width 2), so playlists still sort correctly past day 99.
    day_width = max(2, len(str(days)))

    # Start Study_plan.txt fresh.
    open(os.path.join(directory, "Study_plan.txt"), "w", encoding="utf-8").close()

    for list_vid in videos:
        for vid in videos[list_vid]:
            if length_in_seconds > 0:
                study_list.append(f"{list_vid};{vid[0]}")
                length_in_seconds -= vid[1]
                current_length += vid[1]
            else:
                # Fast-forward past any days the user wants to skip entirely
                # (the pending video is NOT lost -- it carries over below).
                while date_time_obj.strftime("%a").lower() in skipped_days:
                    date_time_obj += timedelta(days=1)

                formatted_date = date_time_obj.strftime("%A %d %B %Y")
                write_to_file(study_list, current_length, day_num, formatted_date, directory, day_width)

                date_time_obj += timedelta(days=1)
                day_num += 1
                study_list = [f"{list_vid};{vid[0]}"]
                current_length = vid[1]
                length_in_seconds = study_time - vid[1]

    # Write out whatever's left over as the final day.
    if study_list:
        while date_time_obj.strftime("%a").lower() in skipped_days:
            date_time_obj += timedelta(days=1)
        formatted_date = date_time_obj.strftime("%A %d %B %Y")
        write_to_file(study_list, current_length, day_num, formatted_date, directory, day_width)

    plan_path = os.path.join(directory, "Study_plan.txt")
    with open(plan_path, 'r+', encoding="utf-8") as f:
        content = f.read()
        line = (
            f"Your study plan consists of approximately {minutes_per_day} minutes "
            f"for {day_num} days"
        )
        f.seek(0, 0)
        f.write(line + '\n' + content)

    return day_num, minutes_per_day
    