# img-to-turtle
Shows every addon installed locally on the users machine for a specified game.

Requires the requests library, install it with
`python3 -m pip install --upgrade requests`.

## Obtaining an API key
To make requests to the Steam Web API for collecting workshop data, you will need a Steam Web API Key. To obtain one, visit https://steamcommunity.com/dev/apikey. You will need the Steam Mobile Authenticator enabled. When registering, it will prompt you for a domain name. If you do not own a domain, feel free to put anything in this field. Afterwards, you will receive a Base64 encoded string as your key. Put this key in the .env file under `STEAM_WEB_API_KEY=`.