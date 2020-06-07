from app.routes.company import company_routes
from app.routes.mailbox import mailbox_routes
from app.routes.news import news_routes
from app.routes.town import town_routes
from app.routes.vehicle import vehicle_routes


def register_routes(app, api):
    app.register_blueprint(company_routes)
    app.register_blueprint(mailbox_routes)
    app.register_blueprint(news_routes)
    app.register_blueprint(town_routes)
    app.register_blueprint(vehicle_routes)

    api.register_blueprint(company_routes)
    api.register_blueprint(mailbox_routes)
    api.register_blueprint(news_routes)
    api.register_blueprint(town_routes)
    api.register_blueprint(vehicle_routes)
