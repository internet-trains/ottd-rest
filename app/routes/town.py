from http import HTTPStatus

from flask_smorest import Blueprint
from app.models.town import Town
from app.models.timescale_mixin import TimeScaleRequestSchema
from app.schemas.town import TownSchema, TownGrowSchema, TownNameSchema, TownTextSchema
from app import ottd_connection

town_routes = Blueprint(
    "Town", __name__, url_prefix="/town", description="Routes for getting town data."
)


@town_routes.route("/", methods=["GET"])
@town_routes.response(TownSchema(many=True), code=HTTPStatus.OK)
def list():
    """
    Lists all towns and their details
    ---
    :return:
    """
    return Town.query.all(), HTTPStatus.OK


@town_routes.route("/<int:town_id>", methods=["GET"])
@town_routes.response(TownSchema(), code=HTTPStatus.OK)
def get_by_id(town_id):
    """
    Gets a town's details by id
    ---
    :param town_id:
    :return:
    """
    return Town.query.filter_by(id=town_id).first_or_404(), HTTPStatus.OK

@town_routes.route("/<int:town_id>/grow", methods=["POST"])
@town_routes.arguments(TownGrowSchema, location="query", as_kwargs=True)
@town_routes.response(code=HTTPStatus.OK)
def send_to_depot(town_id, **kwargs):
    """
    Grows a town by the specified number of houses
    ---
    :return:
    """
    town = Town.query.filter(Town.id == town_id).first_or_404()

    mailbox = ottd_connection.grow_town(town_id, kwargs['houses'])

    return {"status": True, "mailbox": mailbox}, HTTPStatus.OK


@town_routes.route("/<int:town_id>/name", methods=["POST"])
@town_routes.arguments(TownNameSchema, location="query", as_kwargs=True)
@town_routes.response(code=HTTPStatus.OK)
def send_to_depot(town_id, **kwargs):
    """
    Sets the name of a town.
    ---
    :return:
    """
    town = Town.query.filter(Town.id == town_id).first_or_404()

    mailbox = ottd_connection.rename_town(town_id, kwargs['name'])

    return {"status": True, "mailbox": mailbox}, HTTPStatus.OK


@town_routes.route("/<int:town_id>/text", methods=["POST"])
@town_routes.arguments(TownTextSchema, location="query", as_kwargs=True)
@town_routes.response(code=HTTPStatus.OK)
def send_to_depot(town_id, **kwargs):
    """
    Sets the town text.
    ---
    :return:
    """
    town = Town.query.filter(Town.id == town_id).first_or_404()

    mailbox = ottd_connection.set_town_text(town_id, kwargs['text'])

    return {"status": True, "mailbox": mailbox}, HTTPStatus.OK


@town_routes.route("/timescale_data")
@town_routes.arguments(TimeScaleRequestSchema, location="query", as_kwargs=True)
@town_routes.response(Town.timescale_schema()(many=True), code=HTTPStatus.OK)
def all_companies_timescale(**kwargs):
    """
    Gets the timescale data of all towns
    ---
    :return:
    """
    query = Town.timescale_type.query

    if "start" in kwargs:
        query = query.filter(Town.timescale_type.timestamp >= kwargs["start"])
    if "end" in kwargs:
        query = query.filter(Town.timescale_type.timestamp <= kwargs["end"])

    return query.all(), HTTPStatus.OK


@town_routes.route("/<int:town_id>/timescale_data", methods=["GET"])
@town_routes.arguments(TimeScaleRequestSchema, location="query", as_kwargs=True)
@town_routes.response(Town.timescale_schema()(many=True), code=HTTPStatus.OK)
def town_timescale(town_id, **kwargs):
    """
    Gets the timescale data of one town
    ---
    :param town_id:
    :return:
    """
    town = Town.query.filter_by(id=town_id).first_or_404()

    query = town.timescale_type.query.filter_by(town_id=town_id)

    if "start" in kwargs:
        query = query.filter(town.timescale_type.timestamp >= kwargs["start"])
    if "end" in kwargs:
        query = query.filter(town.timescale_type.timestamp <= kwargs["end"])

    return query.order_by(town.timescale_type.timestamp).all(), HTTPStatus.OK
