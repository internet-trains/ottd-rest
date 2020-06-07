from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_smorest import Api

import threading
import atexit
import sys
from flask import Flask

POOL_TIME = 1  # Seconds
TIMESCALE_POOL_TIME = 1


dataLock = threading.Lock()
connection_thread = threading.Thread()
timescale_updater_thread = threading.Thread()

ottd_connection = None
current_date = None

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
migrate = Migrate(app, db)

from app.controllers.ottd import OpenTTDConnection  # noqa
from app.controllers.company import CompanyTimescaleController  # noqa


def interrupt():
    global connection_thread
    connection_thread.cancel()


def do_connection_thread():
    global connection_thread
    global ottd_connection
    global current_date
    with dataLock:
        # Do your stuff with commonDataStruct Here
        ottd_connection.req_data()
        current_date = ottd_connection.sync_data()()
        print(current_date)

    # Set the next thread to happen
    connection_thread = threading.Timer(POOL_TIME, do_connection_thread, ())
    connection_thread.start()


def start_connection_thread():
    # Do initialisation stuff here
    global connection_thread
    global ottd_connection
    # Create your thread
    connection_thread = threading.Timer(POOL_TIME, do_connection_thread, ())
    ottd_connection = OpenTTDConnection()
    connection_thread.start()


def start_timescale_thread():
    global timescale_updater_thread
    timescale_updater_thread = threading.Timer(
        TIMESCALE_POOL_TIME, do_timescale_thread, ()
    )
    timescale_updater_thread.start()


def do_timescale_thread():
    global timescale_updater_thread
    global current_date
    CompanyTimescaleController.capture_data(current_date)
    timescale_updater_thread = threading.Timer(
        TIMESCALE_POOL_TIME, do_timescale_thread, ()
    )
    timescale_updater_thread.start()

# Only run tasks if flask is being run.
flask = "flask/__main__.py"

if sys.argv[0][-len(flask):] == flask and sys.argv[1] == 'run':
    # Initiate
    start_connection_thread()
    start_timescale_thread()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)


from app import routes, models

routes.register_routes(app, api)
