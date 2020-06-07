from http import HTTPStatus

from flask_smorest import Blueprint
from app.models.company import Company
from app.models.timescale_mixin import TimeScaleRequestSchema
from app.schemas.company import CompanySchema
from app import ottd_connection

mailbox_routes = Blueprint("Mailboxes", __name__, url_prefix="/mailbox", description="Routes sending + recieving results from Gamescript Functions")


@mailbox_routes.route("/<int:mailbox_id>", methods=["GET"])
@mailbox_routes.response(code=HTTPStatus.OK)
def list(mailbox_id):
    '''
    Gets contents of a mailbox.
    ---
    :return:
    '''
    return ottd_connection.get_mailbox(mailbox_id), HTTPStatus.OK

# @mailbox_routes.route("/", methods=["POST"])
# @mailbox_routes.response(code=HTTPStatus.OK)
# def list():
#     '''
#     Requests V details.
#     ---
#     :return:
#     '''
#     mailbox_id = ottd_connection.get_vehicle_details(1,1)
#     return {'mailbox_id': mailbox_id}, HTTPStatus.CREATED