from http import HTTPStatus

from flask_smorest import Blueprint
from app.models.company import Company
from app.models.timescale_mixin import TimeScaleRequestSchema
from app.schemas.company import CompanySchema

company_routes = Blueprint("Company", __name__, url_prefix="/company", description="Routes for getting company data.")


@company_routes.route("/", methods=["GET"])
@company_routes.response(CompanySchema(many=True), code=HTTPStatus.OK)
def list():
    '''
    Lists all companies and their details
    ---
    :return:
    '''
    return Company.query.all(), HTTPStatus.OK


@company_routes.route("/<int:company_id>", methods=["GET"])
@company_routes.response(CompanySchema(), code=HTTPStatus.OK)
def get_by_id(company_id):
    '''
    Gets a company's details by id
    ---
    :param company_id:
    :return:
    '''
    return Company.query.filter_by(id=company_id).first_or_404(), HTTPStatus.OK


@company_routes.route("/timescale_data")
@company_routes.arguments(TimeScaleRequestSchema, location='query', as_kwargs=True)
@company_routes.response(Company.timescale_schema(many=True), code=HTTPStatus.OK)
def all_companies_timescale(**kwargs):
    '''
    Gets the timescale data of all companies
    ---
    :return:
    '''
    query = Company.timescale_type.query

    if 'start' in kwargs:
        query = query.filter(Company.timescale_type.timestamp >= kwargs['start'])
    if 'end' in kwargs:
        query = query.filter(Company.timescale_type.timestamp <= kwargs['end'])

    return query.all(), HTTPStatus.OK


@company_routes.route("/<int:company_id>/timescale_data", methods=["GET"])
@company_routes.arguments(TimeScaleRequestSchema, location='query', as_kwargs=True)
@company_routes.response(Company.timescale_schema(many=True), code=HTTPStatus.OK)
def company_timescale(company_id, **kwargs):
    '''
    Gets the timescale data of one company
    ---
    :param company_id:
    :return:
    '''
    company = Company.query.filter_by(id=company_id).first_or_404()

    query = company.timescale_type.query.filter_by(company_id=company_id)

    if 'start' in kwargs:
        query = query.filter(company.timescale_type.timestamp >= kwargs['start'])
    if 'end' in kwargs:
        query = query.filter(company.timescale_type.timestamp <= kwargs['end'])

    return query.all(), HTTPStatus.OK