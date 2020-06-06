from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_smorest import Api

import threading
import atexit
from flask import Flask

POOL_TIME = 5  # Seconds

# variables that are accessible from anywhere
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()

ottd_connection = None

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
migrate = Migrate(app, db)

from app.controllers.ottd import OpenTTDConnection # noqa

def interrupt():
    global yourThread
    yourThread.cancel()


def doStuff():
    global commonDataStruct
    global yourThread
    global ottd_connection
    with dataLock:
        # Do your stuff with commonDataStruct Here
        ottd_connection.req_data()
        ottd_connection.sync_data()

    # Set the next thread to happen
    yourThread = threading.Timer(POOL_TIME, doStuff, ())
    yourThread.start()


def doStuffStart():
    # Do initialisation stuff here
    global yourThread
    global ottd_connection
    # Create your thread
    yourThread = threading.Timer(POOL_TIME, doStuff, ())
    ottd_connection = OpenTTDConnection()
    yourThread.start()


# Initiate
doStuffStart()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)


from app import routes, models

routes.register_routes(app)
