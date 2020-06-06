from http import HTTPStatus

from flask_smorest import Blueprint
from app.models.company import Company
from app.schemas.company import CompanySchema

company_routes = Blueprint("", __name__, url_prefix="/company")


@company_routes.route("/", methods=["GET"])
@company_routes.response(CompanySchema(many=True), code=HTTPStatus.OK)
def list():
    return Company.query.all(), HTTPStatus.OK


@company_routes.route("/<int:company_id>", methods=["GET"])
@company_routes.response(CompanySchema(), code=HTTPStatus.OK)
def list(company_id):
    return Company.query.filter_by(id=company_id).first_or_404(), HTTPStatus.OK
