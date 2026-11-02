# Study Plan

A small Python tool that turns a folder of course videos into a day-by-day
study schedule. Point it at a course directory, tell it how much time you have,
and it splits the videos into daily chunks, writes a human-readable plan, and
generates an `.m3u` playlist for each day so you can just press play.

It was built for people who download lecture series (e.g. from a course
platform) and want to spread them out over a fixed number of days or a fixed
number of minutes per day — without manually counting video lengths.

---

## What it does

Given a course directory laid out like this:

```
MyCourse/
├── 01 Introduction/
│   ├── 1. Welcome.mp4
│   └── 2. Course overview.mp4
├── 02 Basics/
│   ├── 1. Variables.mp4
│   └── 2. Loops.mp4
└── 03 Advanced/
    └── 1. Functions.mp4
```

the script will:

1. Scan every module subfolder for video files
   (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.m4v`).
2. Read each video's duration using OpenCV.
3. Split the videos into daily study sessions based on your chosen duration.
4. Write `Study_plan.txt` into the course folder — a plain-text, day-by-day list.
5. Write one `.m3u` playlist per day into `MyCourse/playlists/`, so a media
   player can play that day's videos in order.

---

## Requirements

- Python 3.8+
- [OpenCV for Python](https://pypi.org/project/opencv-python/) (`cv2`)

Install the dependency:

```bash
pip install opencv-python
```

> The repository does not ship a `requirements.txt`; `opencv-python` is the only
> third-party package used.

---

## Usage

Run the main script:

```bash
python main.py
```

You will be prompted for:

| Prompt                             | Meaning                                                             |
| ---------------------------------- | ------------------------------------------------------------------- |
| Full path of your course           | Absolute path to the folder containing module subfolders.           |
| How many modules to skip           | Number of leading module folders (sorted alphabetically) to ignore. |
| Days to skip                       | Space-separated weekday abbreviations, e.g. `sat sun`.              |
| Start date                         | `yyyy-mm-dd`, e.g. `2026-07-15`.                                    |
| Days or time (`d`/`t`)             | Plan by a number of days, or by minutes per day.                    |
| If `d`: days or end date (`d`/`e`) | Study for N days, or until a given end date.                        |
| If `t`: minutes per day            | How long each daily session should be.                              |

### Example session

```
Enter full path of your course: /home/me/MyCourse
How many modules would you like to skip: 0
Enter the days you would want to skip (sun mon tue wed thu fri sat): sat sun
When would you like to start? enter date in format of yyyy-mm-dd: 2026-07-15
Do you want your study plan to be in days or time? (d/t): d
Would you like to enter the days(d) or the end date(e) (d/e): d
How many days do you want to study for: 10
```

### Output

`MyCourse/Study_plan.txt`:

```
Your study plan consists of approximately 42 minutes for 10 days

Day 1
Wednesday 15 July 2026
Todays study videos consists of approximately 42 minutes
1. Welcome.mp4
2. Course overview.mp4
...
```

`MyCourse/playlists/01. Wednesday 15 July 2026.m3u`:

```
/home/me/MyCourse/01 Introduction/1. Welcome.mp4
/home/me/MyCourse/01 Introduction/2. Course overview.mp4
```

Open the `.m3u` file in VLC (or any media player) to play that day's videos.

---

## How it works

| File                                       | Responsibility                                                                                       |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| [`main.py`](main.py)                       | Interactive entry point. Collects user input, validates it, and calls the helpers.                   |
| [`functions.py`](functions.py)             | Core logic: scanning videos, reading durations, splitting into days, writing the plan and playlists. |
| [`renaming_script.py`](renaming_script.py) | Standalone helper that zero-pads numeric filenames (e.g. `1.mp4` → `01.mp4`) so they sort correctly. |

### Execution flow

1. `main.py` prompts for the course path and validates it exists.
2. `list_files()` in `functions.py` walks the module subfolders, finds video
   files, and reads each duration with OpenCV (`_get_video_duration`).
   Durations are cached in `.duration_cache.json` inside the course folder so
   re-runs are fast.
3. `study_plan()` calculates how much video goes into each day, then calls
   `write_to_file()` for each day.
4. `write_to_file()` appends the day to `Study_plan.txt` and writes the
   matching `.m3u` playlist.
5. `main.py` prints a short summary.

---

## Renaming helper (optional)

If your video files are numbered inconsistently (`1.mp4`, `2.mp4`, `10.mp4`),
they may sort incorrectly. Run:

```bash
python renaming_script.py
```

It asks for the file extension, the course path, and the separator used before
the number (`.` or `-`), then shows a preview of the renames and asks for
confirmation before changing anything.

---

## Notes and limitations

- Only files with the extensions listed above are treated as videos.
- Videos that cannot be read (corrupted or unsupported codec) are skipped with
  a warning.
- The script overwrites an existing `Study_plan.txt` and clears the
  `playlists/` folder for that course each run (it asks before overwriting the
  plan).
- The `.m3u` playlists use absolute paths, so they are tied to the machine and
  folder location where the plan was generated.
- There is no packaging or install step; it is run directly with `python`.
