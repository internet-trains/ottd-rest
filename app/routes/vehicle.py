from http import HTTPStatus

from flask_smorest import Blueprint
from app.extensions import db
from app.controllers.vehicle import VehicleController
from app.models.vehicle import Vehicle
from app.models.timescale_mixin import TimeScaleRequestSchema
from app.schemas.vehicle import VehicleSchema
from app import ottd_connection

vehicle_routes = Blueprint(
    "Vehicles",
    __name__,
    url_prefix="/vehicle",
    description="Routes for reading stored vehicle data.",
)

@vehicle_routes.route("/", methods=["GET"])
@vehicle_routes.response(VehicleSchema(many=True), code=HTTPStatus.OK)
def get():
    """
    Gets stored information about a vehicle.
    ---
    :return:
    """

    return Vehicle.query.all(), HTTPStatus.OK

@vehicle_routes.route("/<int:vehicle_id>", methods=["GET"])
@vehicle_routes.response(VehicleSchema(), code=HTTPStatus.OK)
def get(vehicle_id):
    """
    Gets stored information about a vehicle.
    ---
    :return:
    """

    return Vehicle.query.filter(Vehicle.id == vehicle_id).first_or_404(), HTTPStatus.OK


@vehicle_routes.route("/<int:vehicle_id>/register", methods=["PUT"])
@vehicle_routes.response(code=HTTPStatus.OK)
def register(vehicle_id):
    """
    Starts updating for a specific vehicle ID
    ---
    :return:
    """
    vehicle = Vehicle.query.filter(Vehicle.id == vehicle_id).first()

    if vehicle:
        return "", HTTPStatus.CONFLICT

    vehicle = Vehicle(id=vehicle_id)
    db.session.add(vehicle)
    db.session.commit()
    mailboxes = VehicleController.update_by_id(ottd_connection, vehicle_id)

    return {"status": True, "mailboxes": mailboxes}, HTTPStatus.OK

# TODO: Sort out concurrency issues here.

@vehicle_routes.route("/<int:vehicle_id>/send_to_depot", methods=["POST"])
@vehicle_routes.response(code=HTTPStatus.OK)
def send_to_depot(vehicle_id):
    """
    Send vehicle to depot
    ---
    :return:
    """
    Vehicle.query.filter(Vehicle.id == vehicle_id).first_or_404()

    mailbox = ottd_connection.send_vehicle_to_depot(vehicle_id)

    return {"status": True, "mailbox": mailbox}, HTTPStatus.OK


@vehicle_routes.route("/<int:vehicle_id>/send_for_service", methods=["POST"])
@vehicle_routes.response(code=HTTPStatus.OK)
def send_to_depot(vehicle_id):
    """
    Send vehicle to depot
    ---
    :return:
    """
    vehicle = Vehicle.query.filter(Vehicle.id == vehicle_id).first_or_404()

    mailbox = ottd_connection.send_vehicle_for_service(vehicle_id, vehicle.company_id)

    return {"status": True, "mailbox": mailbox}, HTTPStatus.OK


@vehicle_routes.route("/<int:vehicle_id>/update", methods=["PUT"])
@vehicle_routes.response(VehicleSchema(), code=HTTPStatus.OK)
def update(vehicle_id):
    """
    Requests an update ASAP for a vehicle
    ---
    :return:
    """
    vehicle = Vehicle.query.filter(Vehicle.id == vehicle_id).first_or_404()
    mailboxes = VehicleController.update_by_id(ottd_connection, vehicle_id)
    return {"status": True, "mailboxes": mailboxes}, HTTPStatus.OK


@vehicle_routes.route("/<int:vehicle_id>/timescale_data", methods=["GET"])
@vehicle_routes.arguments(TimeScaleRequestSchema, location="query", as_kwargs=True)
@vehicle_routes.response(Vehicle.timescale_schema()(many=True), code=HTTPStatus.OK)
def vehicle_timescale(vehicle_id, **kwargs):
    """
    Gets the timescale data of one company
    ---
    :param vehicle_id:
    :return:
    """
    vehicle = Vehicle.query.filter_by(id=vehicle_id).first_or_404()

    query = vehicle.timescale_type.query.filter_by(vehicle_id=vehicle_id)

    if "start" in kwargs:
        query = query.filter(vehicle.timescale_type.timestamp >= kwargs["start"])
    if "end" in kwargs:
        query = query.filter(vehicle.timescale_type.timestamp <= kwargs["end"])

    return query.order_by(vehicle.timescale_type.timestamp).all(), HTTPStatus.OK
