Python script that walks through the directories and store their files information into Sqlite database.
Python 3 is required for that script. Tested on Linux environment. Can handle big files and does not overload your system much.

How to use the script?

Run it with -d parameter and directory or path to directory you want to go through.

Example:
python3 db_collect.py -d your_dir

Script also understands absolute paths, so you can specify it.

Example:python3 db_collect.py -d /home/user/your_dir

To compare records from the database with real files, run the script without any parameters. It would walk through all mentioned in DB files and create a report within 'log' directory. Log directory is located next to the script file.
