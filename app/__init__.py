from time import sleep

from flask import Flask
from app.extensions import init_extensions
from app.commands import cli_commands
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_smorest import Api
from flask_cors import CORS

from logging import info
import threading
import atexit
import sys
from flask import Flask
from flaskthreads import AppContextThread

POOL_TIME = 1  # Seconds
TIMESCALE_POOL_TIME = 1

dataLock = threading.Lock()
connection_thread = None
timescale_updater_thread = None

ottd_connection = None  # type: OpenTTDConnection
current_date = None
month_last_update = None
year_last_update = None


def init_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    api = Api(app)
    init_extensions(app)

    app.cli.add_command(cli_commands)

    from app.controllers.ottd import OpenTTDConnection  # noqa
    from app.controllers.company import CompanyTimescaleController  # noqa
    from app.controllers.vehicle import VehicleTimescaleController, VehicleController
    from app.controllers.town import TownController, TownTimescaleController

    def interrupt():
        global connection_thread
        global timescale_updater_thread
        connection_thread.cancel()
        timescale_updater_thread.cancel()

    def do_connection_thread():
        sleep(1)
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
        connection_thread = AppContextThread(target=do_connection_thread)
        connection_thread.start()

    def start_connection_thread(app):
        # Do initialisation stuff here
        global connection_thread
        global ottd_connection
        # Create your thread
        with app.app_context():
            connection_thread = AppContextThread(target=do_connection_thread)
            ottd_connection = OpenTTDConnection()
            # ottd_connection.scan_vehicles(20)
            info(f" [ Start Town Scan ]")
            ottd_connection.schedule_next_town_scan_batch(0, 10)
            connection_thread.start()

    def start_timescale_thread(app):
        global timescale_updater_thread
        with app.app_context():
            timescale_updater_thread = AppContextThread(
                target=do_timescale_thread
            )
            timescale_updater_thread.start()

    def do_timescale_thread():
        sleep(1)
        global timescale_updater_thread
        global current_date
        CompanyTimescaleController.capture_data(current_date)
        VehicleTimescaleController.capture_data(current_date)
        TownTimescaleController.capture_data(current_date)
        timescale_updater_thread = AppContextThread(
            target=do_timescale_thread
        )
        timescale_updater_thread.start()

    # Only run tasks if flask is being run.
    flask = "flask/__main__.py"

    if sys.argv[0][-len(flask):] == flask and sys.argv[1] == "run":
        # Initiate
        start_connection_thread(app)
        # start_timescale_thread(app)
        # When you kill Flask (SIGTERM), clear the trigger for the next thread
        atexit.register(interrupt)

    from app import routes, models

    routes.register_routes(app, api)

    return app