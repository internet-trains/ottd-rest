# ottd-rest
Simple OpenTTD GameScript HTTP Binding with a Quart Microservice.

## Installation
### Prerequisites
* OpenTTD + OpenTTD Source for your installed version
* [Latest version of ServerGS (from hg repo)](http://dev.openttdcoop.org/projects/gs-server/repository)
* A Python 2.7 installation (for building ServerGS bindings)
* A Python 3.7 installation (for running Quart Service)
### Building ServerGS Bindings
* Edit `gen_api_binding.py`
    * Set `openttd_path` to your openttd path (`/Users/ian/Downloads/OpenTTD-patches-jgrpp-0.34.3` for me)
    * Set `gs_path` to your gamescript folder path (`src/script/api/game` for me)
    * Set `version` to your version (string).
* Run `gen_api_binding.py` with your python2.7 installation. 
* Copy the enclosing folder to your gamescript folder path.
