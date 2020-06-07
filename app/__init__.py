from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_smorest import Api

from logging import info
import threading
import atexit
import sys
from flask import Flask

POOL_TIME = 1  # Seconds
TIMESCALE_POOL_TIME = 1

dataLock = threading.Lock()
connection_thread = threading.Thread()
timescale_updater_thread = threading.Thread()

ottd_connection = None  # type: OpenTTDConnection
current_date = None
month_last_update = None
year_last_update = None

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
migrate = Migrate(app, db)

from app.controllers.ottd import OpenTTDConnection  # noqa
from app.controllers.company import CompanyTimescaleController  # noqa
from app.controllers.vehicle import VehicleTimescaleController, VehicleController
from app.controllers.town import TownController


def interrupt():
    global connection_thread
    global timescale_updater_thread
    connection_thread.cancel()
    timescale_updater_thread.cancel()


def do_connection_thread():
    global connection_thread
    global ottd_connection
    global current_date
    global month_last_update
    global year_last_update

    with dataLock:
        # Do your stuff with commonDataStruct Here
        ottd_connection.req_data()
        current_date = ottd_connection.sync_data()()
        if month_last_update != current_date.month:
            # Trigger Vehicle Sync
            info(f" [ New Month {current_date.year}-{current_date.month} ]")
            info(f" [ Requesting City Updates ] ")
            # VehicleController.trigger_sync_tasks(ottd_connection)
            ottd_connection.refresh_db_vehicles()
            ottd_connection.refresh_db_towns()
            month_last_update = current_date.month
        if year_last_update != current_date.year:
            info(f" [ New Year {current_date.year} ] ")
            year_last_update = current_date.year

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
    # ottd_connection.scan_vehicles(20)
    info(f" [ Start Town Scan ]")
    ottd_connection.schedule_next_town_scan_batch(0, 10)
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
    VehicleTimescaleController.capture_data(current_date)
    timescale_updater_thread = threading.Timer(
        TIMESCALE_POOL_TIME, do_timescale_thread, ()
    )
    timescale_updater_thread.start()


# Only run tasks if flask is being run.
flask = "flask/__main__.py"

if sys.argv[0][-len(flask) :] == flask and sys.argv[1] == "run":
    # Initiate
    start_connection_thread()
    start_timescale_thread()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)


from app import routes, models

routes.register_routes(app, api)
