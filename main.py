import os
from datetime import datetime
from functions import list_files, study_plan


def prompt_int(prompt_text, minimum=None):
    while True:
        raw = input(prompt_text)
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Please enter a number of at least {minimum}.")
            continue
        return value


def prompt_date(prompt_text):
    while True:
        raw = input(prompt_text)
        try:
            datetime.strptime(raw, '%Y-%m-%d')
            return raw
        except ValueError:
            print("Please enter the date in yyyy-mm-dd format, e.g. 2026-07-15.")


def prompt_choice(prompt_text, valid_choices):
    while True:
        raw = input(prompt_text).strip().lower()
        if raw in valid_choices:
            return raw
        print(f"Please enter one of: {', '.join(valid_choices)}")


directory = input("Enter full path of your course: ").strip()
while not os.path.isdir(directory):
    print("That directory doesn't exist.")
    directory = input("Enter full path of your course: ").strip()

skipped_modules = prompt_int(
    "How many modules would you like to skip: ", minimum=0
)
skip_days = input(
    "Enter the days you would want to skip, enter space for multiple days"
    "(sun mon tue wed thu fri sat): "
).lower()
start_date = prompt_date("When would you like to start? enter date in format of yyyy-mm-dd: ")
duration_choice = prompt_choice(
    "Do you want your study plan to be in days or time? (d/t): ", ["d", "t"]
)

if duration_choice == "d":
    type_of_date = prompt_choice(
        "Would you like to enter the days(d) or the end date(e) (d/e): ", ["d", "e"]
    )
    if type_of_date == "d":
        length = prompt_int("How many days do you want to study for: ", minimum=1)
    else:
        length = prompt_date("When would you like to end the course? enter date in format of yyyy-mm-dd: ")
        if length <= start_date:
            print("The end date must be after the start date.")
            raise SystemExit(1)
else:
    length = prompt_int("How long do you study each day, enter time in minutes: ", minimum=1)

# Warn before wiping out an existing plan/playlists for this course.
existing_plan = os.path.join(directory, "Study_plan.txt")
if os.path.exists(existing_plan):
    confirm = input(
        "A Study_plan.txt already exists in this directory and will be overwritten. "
        "Continue? (y/n): "
    ).strip().lower()
    if confirm != "y":
        print("Cancelled.")
        raise SystemExit(0)

try:
    videos = list_files(directory, skipped_modules)
    day_num, minutes_per_day = study_plan(
        videos, length, duration_choice, start_date, directory, skip_days
    )
except (FileNotFoundError, ValueError) as exc:
    print(f"Couldn't generate a study plan: {exc}")
    raise SystemExit(1)

print(
    f"Your study plan has been generated ({day_num} day(s), "
    f"~{minutes_per_day} minutes/day). You'll find it in your course directory."
)