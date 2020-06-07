from app.routes.company import company_routes


def register_routes(app, api):
    app.register_blueprint(company_routes)
    api.register_blueprint(company_routes)
