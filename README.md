# ottd-rest
Simple OpenTTD GameScript HTTP Binding and Game Logger with a Flask Microservice.

Have you ever found OpenTTD's in-game stats to be insufficient and inaccessible? 
This piece of software aims to fix that. 
Stats are collected continuously, and saved to a database of your choice. 
Stats are are also accessible via HTTP endpoints.

## Installation
### Prerequisites
* OpenTTD + OpenTTD Source for your installed version
* [ServerGS (internet-trains fork)](https://github.com/internet-trains/ServerGS)
* A Python 3.7+ installation (for running Flask Service + Generating Bindings)
* _(optional) A Database_ ([supported](https://docs.sqlalchemy.org/en/13/dialects/))
### Building ServerGS Bindings
* Edit `gen_api_binding.py`
    * Set `openttd_path` to your openttd path (`/Users/ian/Downloads/OpenTTD-patches-jgrpp-0.34.3` for me)
    * Set `gs_path` to your gamescript folder path (`src/script/api/game` for me)
    * Set `version` to your version (string).
* Run `gen_api_binding.py` with your python installation. 
* Copy the enclosing folder to your gamescript folder path.

### Python Prerequisites
* Run `python3 -m pip install -r requirements.txt`
### DB Setup
* Set your `SQLALCHEMY_DATABASE_URI` environment variable to your db's uri.
* Run the following commands.
```bash
export FLASK_APP=ottd.py

python3 -m flask db init
python3 -m flask db upgrade
```
## Generate Doc
```bash
python3 -m ./gen_doc.py
```
## Running
Optional, if you wish to use something other than an SqliteDb:
```bash
export DATABASE_URL=YOUR_DATABASE_URI
```
Then run
```bash
export FLASK_APP=ottd.py
export OTTD_GS_HOST=127.0.0.1
export OTTD_GS_PORT=3977
export OTTD_GS_PASSWORD=password 
python3 -m flask run -p 5000
```
## Doc
Doc is hosted at `http://localhost:5000/swagger-ui` or `http://localhost:5000/redoc` when the server 
is running. `api.json` can also be used with other OpenAPI doc toolpythos.
