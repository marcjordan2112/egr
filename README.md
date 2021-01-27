# Introduction
ESO Grinder (EGR) is an Elder Scrolls Online addon that monitors loot and saves it to the user's ESO save file. The ESO Save File Monitor (ESFM) Python code polls the save file every 3 seconds and if new loot is found then adds it to a user-specified database.

The user first runs the ESFM Python script on a command line (CL), specifying the user's ESO @PlayerName, path to ESO save file, and path to the database file. Then the user simply plays ESO (with the EGR addon installed) and "it just works" :) All items added to the database are shown in the EFSM output window. Currently, it's up to the user to decide what to do with the database.

EGR was inspired by https://forums.elderscrollsonline.com/en/discussion/comment/5259194/#Comment_5259194

# Important
- Wait at least 3 seconds after closing ESO, reloading the UI, or logging out before you close an ESFM instance. 

# ESO Grinder

## Installation

Copy this entire directory into 

    <?>\Elder Scrolls Online\live\AddOns\EsoGrinder

Please search the internet to find details on the AddOns directory location for your OS. 

## Usage

In-game console commands:

- /egrstart Start EGR.
- /egrstop Stop EGR.
- /egrdebug Toggle debug.
- /egrapiversion Show ESO API version. Debug must be enabled to see output.

todo:

- [x]  Pull in addon args, define usage in one place.

## Notes
- The database is created automatically if it does not exist.

## Limitations
###  When does ESO write user's save file?
I have noticed that the ESO save file is always written under these conditions:

- Run the /reloadui command
- Logout
- Exit
- Randomly

Teleports don't seem to reliably do it. If you notice other predictable conditions please let me know.

### Loot Item Logging
- Logged
    - Quest reward
    - Searched
    - Mined
    - Collected
    - Taken
    - Fished
- Not Logged:
    - Gold (currency, not item quality)
    - Mail
    - Creation
    - Traded

# ESO Save File Monitor

## Installation
Run the following to install 

    $pip install -r requirements.txt

## Usage

Run

    $python eso_save_file_monitor.py -h
    
todo:

- [x]  Pull in python args, define usage in one place.

## Database
The EFSM database is a standard SQLite database. It may be viewed by any standard SQLite tools.

If opening the database with a tool then open as read-only, otherwise there will be conflicts with the EFSM at run time.

# Change List

- 2.0.0
    - Change the name of the installation file/directory from "egr-x.x.x" to "EsoGrinder".
        - To preserve existing databases you can copy/paste them from an existing ".../Addons/egr-x.x.x" to the new 
        ".../Addons/EsoGrinder" directory.
    - Remove old temporary dev files.
    - Update README.md value of poll time from 5 to 3 seconds. It has always been 3 seconds.
    - Update EsoGrinder.txt to fix esoui/minion issues.

- 1.0.2
    - Remove dev debug prints.

- 1.0.1
    - Add .gitignore.
    - Update API version to 100033.
    - Add /egrapiversion utility command.
    
- 1.0.0
    - Initial release for ESO Api version .

