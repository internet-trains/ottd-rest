from http import HTTPStatus

from flask_smorest import Blueprint
from app.models.company import Company
from app.models.timescale_mixin import TimeScaleRequestSchema
from app.schemas.company import CompanySchema
from app import ottd_connection

news_routes = Blueprint(
    "News", __name__, url_prefix="/news", description="Routes for sending news."
)


# @news_routes.route("/", methods=["POST"])
# @news_routes.response(code=HTTPStatus.OK)
# def list():
#     '''
#     Sends news.
#     ---
#     :return:
#     '''
#     mailbox_id = ottd_connection.get_vehicle_details(1,1)
#     return {'mailbox_id': mailbox_id}, HTTPStatus.CREATED
