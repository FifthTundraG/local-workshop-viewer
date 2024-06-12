# === Installed Workshop Viewer ===
# Shows every addon installed LOCALLY on the users machine for a specified game.

import platform # for finding the OS
import os # for finding the IDs of the workshop addons & api key env variables
import logging # For logging important information to the console
from datetime import datetime # For showing the date & time of the output log's info

import requests # for Steam API requests
from dotenv import load_dotenv # For securely storing API keys
import vdf # for finding the library folders automagically

defaultSteamDir: dict[str, str] = {
    "Windows": "C:\\Program Files (x86)\\Steam",
    "Darwin": "~/Library/Application Support", # MacOS
    "Linux": "~/.steam/steam/"
}

def main() -> None:
    logging.basicConfig(format='[%(levelname)s] %(message)s')

    load_dotenv()
    API_KEY: str | None = os.getenv("STEAM_WEB_API_KEY")
    if API_KEY == "" or API_KEY == None:
        logging.critical("No API key was provided in the \".env\" file. See README.md for more details.")
        return

    # Use the libraryfolders.vdf file in "STEAMDIR/steamapps" to find all the library folders
    if platform.system() == "Windows": #* since windows uses backslashes for directory paths, we need to differentiate between them and UNIX-like systems
        libraryfolders = vdf.load(open(defaultSteamDir[platform.system()]+"\\steamapps\\libraryfolders.vdf"))
    else:
        libraryfolders = vdf.load(open(defaultSteamDir[platform.system()]+"/steamapps/libraryfolders.vdf"))
    print("Type the identifier associtated with the Steam library folder your game is installed in:")
    for i in enumerate(libraryfolders["libraryfolders"].keys()):
        print(f"({i[1]}) {libraryfolders["libraryfolders"][i[1]]["path"]}")
    librarySelection = input("Library ID: ")
    if librarySelection not in libraryfolders["libraryfolders"].keys():
        logging.critical("Invalid selection.")
        return
    steamDir = libraryfolders["libraryfolders"][librarySelection]["path"]

    # Get the user's game ID
    GAME_ID = input("Game ID: ") # todo: make this required
    if GAME_ID == None or GAME_ID == "":
        logging.critical("An input for Game ID is required to continue.")
        return
    GAME_ID = int(GAME_ID) #* i can't put this where the input is because we need to check if the input is blank and it will error out complaining that "" isn't a number when it's at definition

    # Using the game ID, get the directory where workshop content is stored
    if platform.system() == "Windows": #* since windows uses backslashes for directory paths, we need to differentiate between them and UNIX-like systems
        workshopDir = f"{steamDir}\\steamapps\\workshop\\content\\{GAME_ID}"
    else:
        workshopDir = f"{steamDir}/steamapps/workshop/content/{GAME_ID}"

    if os.path.exists(workshopDir) != True:
        logging.critical(f"Workshop directory for game {GAME_ID} does not exist. Directory: {workshopDir}")
        return

    # Handle whether we should log to a file
    logToFileInput = input("Would you like to log all addons to a file? Recommended if you have a large amount of addons. [Y/n] ")
    if logToFileInput.lower() == "y": # todo: can this be ternary easily?
        logOutput: bool = True
    elif logToFileInput.lower() == "n":
        logOutput: bool = False
    else:
        logging.error(f"\"{logToFileInput}\" is not a valid response.")
        return
    
    # If output.txt already exists, inform the user and ask if they would like to overwrite
    if os.path.isfile("output.txt") and logOutput:
        fileExistsWarning = input("The output.txt file alrady exists, overwrite it? [Y/n] ")
        if fileExistsWarning.lower() == "y": # todo: can this be ternary easily?
            pass
        elif fileExistsWarning.lower() == "n":
            print("Exiting...")
            return
        else:
            logging.error(f"\"{fileExistsWarning}\" is not a valid response.")
            return
    
    # Make a request to Steam using the game ID to get the name of the game for logging purposes
    gameDetails = requests.get(f'https://store.steampowered.com/api/appdetails?appids={GAME_ID}') # For an example request for gameDetails, use this link for Portal: https://store.steampowered.com/api/appdetails?appids=400
    gameDetails.raise_for_status() 
    if gameDetails.json()[str(GAME_ID)]["success"] != True:
        logging.error("Request to Steam Web API for game id "+str(GAME_ID)+" was not successful.")
        return
    GAME_NAME: str = gameDetails.json()[str(GAME_ID)]["data"]["name"]

    # Get all addon IDs from the workshop content dir and make a request to Steam for their details
    addonIDs: list[str] = next(os.walk(workshopDir))[1] # todo: check if this is none
    fileDetailsURL = f"https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/" # e.x (gmod prop hunt): https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/?key={API_KEY}}&itemcount=1&publishedfileids=135509255
    fileDetailsParams = { # this has all publishedfileids appended to it in the for loop below
        "key": API_KEY,
        "itemcount": len(addonIDs)
    }
    for i in enumerate(addonIDs):
        # todo: figure this out further
        fileDetailsParams[f"publishedfileids[{i[0]}]"] = i[1]
    fileDetails = requests.post(fileDetailsURL, data=fileDetailsParams)
    fileDetails.raise_for_status()
    # we need some way for the error check below to occur, but an error occurs on a sucessful request because the "status" pair isn't there for one
    # if fileDetails.json()["status"]["code"] != 1: # if this field is present then an error occured, 1=OK, any other number is an error
    #     logging.error(f"Request to Steam Web API for workshop data failed. Steam error code {str(fileDetails.json()["status"]["code"])}.")
    #     return

    # Handle writing file and printing output for addon details
    f = open("output.txt", "w", encoding="utf-8") #* we get the following error in certain situations without the encoding bit: UnicodeEncodeError: 'charmap' codec can't encode characters in position 29-36: character maps to <undefined>
    # Write & print title
    msg = f"{GAME_NAME} Local Workshop Addon List - {datetime.now()}\n"
    f.write(f"{msg}\n")
    print(msg)

    addonsWithErrors: list[str] = []
    for i in fileDetails.json()["response"]["publishedfiledetails"]:
        if i["result"] != 1: # 1=OK, any other number is an error
            msg = f"Error while processing addon with ID {i["publishedfileid"]}. Steam error code {i["result"]}"
            print(msg)
            if logOutput: f.write(f"{msg}\n")
            addonsWithErrors.append(i["publishedfileid"])
            continue
        msg = f"{i["title"]} ({i["publishedfileid"]})"
        print(msg)
        if logOutput: f.write(f"{msg}\n")
    f.close()
    print("") # newlines won't work here because the if statement below doesn't always run
    if logOutput: print("Contents have been logged to output.txt.")
    if len(addonsWithErrors) > 0:
        print("There were errors when requesting the following addons:")
        print(addonsWithErrors)
    leaving = input("Press any key to exit... ")

if __name__ == "__main__":
    main()