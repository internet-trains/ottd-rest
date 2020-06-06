from app.routes.company import company_routes


def register_routes(app):
    app.register_blueprint(company_routes)
