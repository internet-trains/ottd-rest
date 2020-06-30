import os
import signal
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

connection_thread = None
timescale_updater_thread = None

ottd_connection = None  # type: OpenTTDConnection
current_date = None
month_last_update = 1
year_last_update = 1

global shutting_down
shutting_down = False

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

    def interrupt(signal_received, frame):
        info("Shutting Down...")
        global shutting_down
        ottd_connection.disconnect()
        shutting_down = True
        sleep(2)
        os.kill(os.getpid(), signal.SIGTERM)

    def do_connection_thread():
        sleep(1)
        global connection_thread
        global ottd_connection
        global current_date
        global month_last_update
        global year_last_update
        global shutting_down

        ottd_connection.req_data()
        current_date = ottd_connection.sync_data()()
        if month_last_update != current_date.month:
            # Trigger Vehicle Sync
            info(f" [ New Month {current_date.year}-{current_date.month} ]")
            info(f" [ Requesting Vehicle Updates ] ")
            ottd_connection.refresh_db_vehicles()
            month_last_update = current_date.month
        if year_last_update != current_date.year:
            info(f" [ New Year {current_date.year} ] ")
            info(f" [ Requesting City & Vehicle Updates ] ")
            year_last_update = current_date.year
            # ottd_connection.refresh_db_vehicles()
            # ottd_connection.refresh_db_towns()

        # Set the next thread to happen
        if not shutting_down:
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
            ottd_connection.schedule_next_town_scan_batch(947, 10)
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
        global shutting_down
        CompanyTimescaleController.capture_data(current_date)
        VehicleTimescaleController.capture_data(current_date)
        TownTimescaleController.capture_data(current_date)
        if not shutting_down:
            timescale_updater_thread = AppContextThread(
                target=do_timescale_thread
            )
            timescale_updater_thread.start()

    # Only run tasks if flask is being run.
    flask = "flask/__main__.py"

    if sys.argv[0][-len(flask):] == flask and sys.argv[1] == "run":
        if not Config.NO_WORKER:
            start_connection_thread(app)
            start_timescale_thread(app)
        signal.signal(signal.SIGINT, interrupt)  # ctlr + c

    from app import routes, models

    routes.register_routes(app, api)

    return app