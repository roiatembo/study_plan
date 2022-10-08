from functions import list_files, study_plan


directory = input("Enter full path of your course: ")
skipped_modules = int(input("How many modules would you like to skip: ")) - 1
start_date = input("when would you like to start? enter date in format of yyyy-mm-dd: ")
duration_choice = input("Do you want your study plan to be in days or time? (d/t): ")

if duration_choice == "d":
    type_of_date = input("Would you like to enter the days(d) or the end date(e) (d/e):")
    if type_of_date == "d":
        length = int(input("How many days do you want to study for: "))
    elif type_of_date == "e":
        length = input("When would you like to end the course? enter date in format of yyyy-mm-dd: ")
elif duration_choice == "t":
    length = int(input("How long do you study each day, enter time in minutes: "))
else:
    print("Uh oh I didn't get that");


videos = list_files(directory, skipped_modules)
study_plan(videos, length, duration_choice, start_date, directory)
print("Your study plan has been generated you will find it in your course directory")
