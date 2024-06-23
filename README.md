# Local Workshop Viewer
Shows every Steam Workshop addon installed locally on the user's machine for a specified game.

Requires the requests, dotenv, and vdf libraries, install them with the following command: <br>
`pip install -r requirements.txt`

## Obtaining an API key
To make requests to the Steam Web API for collecting workshop addon data, you will need a Steam Web API Key. To obtain one, visit https://steamcommunity.com/dev/apikey. You will need the Steam Mobile Authenticator enabled. When registering, it will prompt you for a domain name. If you do not own a domain, feel free to put anything in this field (something like `example.com`). Afterward, you will receive a Base64 encoded string as your key. Make a copy of the `.example.env` file in this project's root directory and name it `.env`. Put your API key in the `.env` file under `STEAM_WEB_API_KEY=`.
### What the API key is used for
The program makes two requests to Steam, one for details regarding the game AppID you entered to show the name of the game in the output (this does NOT require an API key) and the other request is to get the names of the Workshop items the program detects are installed.
