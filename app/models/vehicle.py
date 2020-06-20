from sqlalchemy.orm import relationship

from app.extensions import db
from app.models.timescale_mixin import TimeScaleMixin


class Vehicle(db.Model, TimeScaleMixin):
    timescale_table_value_columns = [
        "running_cost",
        "profit_this_year",
        "value",
        "reliability",
    ]

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    name = db.Column(db.String(64))

    def __repr__(self):
        return f"<Vehicle#{self.id} [{self.name}]>"

    num_wagons = db.Column(db.Integer)
    age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    remaining_life = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    state = db.Column(db.Integer)
    running_cost = db.Column(db.BigInteger)
    profit_this_year = db.Column(db.BigInteger)
    profit_last_year = db.Column(db.BigInteger)
    value = db.Column(db.BigInteger)
    vehicle_type = db.Column(db.Integer)
    road_type = db.Column(db.Integer)
    length = db.Column(db.Float)
    group_id = db.Column(db.Integer)
    is_articulated = db.Column(db.Boolean)
    has_shared_orders = db.Column(db.Boolean)
    reliability = db.Column(db.Float)
    maximum_order_distance = db.Column(db.Integer)
    last_updated = db.Column(db.Date)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    company = relationship('Company')

    gs_map = {
        "GSVehicle.GetOwner": 'company_id',
        # "GSVehicle.GetLocation": 'location',
        # "GSVehicle.GetEngineType",
        # "GSVehicle.GetUnitNumber",
        "GSVehicle.GetNumWagons": "num_wagons",
        "GSVehicle.GetName": "name",
        "GSVehicle.GetAge": "age",
        "GSVehicle.GetMaxAge": "max_age",
        "GSVehicle.GetAgeLeft": "remaining_life",
        "GSVehicle.GetCurrentSpeed": "speed",
        "GSVehicle.GetState": "state",
        "GSVehicle.GetRunningCost": "running_cost",
        "GSVehicle.GetProfitThisYear": "profit_this_year",
        "GSVehicle.GetProfitLastYear": "profit_last_year",
        "GSVehicle.GetCurrentValue": "value",
        "GSVehicle.GetVehicleType": "vehicle_type",
        "GSVehicle.GetRoadType": "road_type",
        "GSVehicle.GetLength": "length",
        "GSVehicle.GetGroupID": "group_id",
        "GSVehicle.IsArticulated": "isArticulated",
        "GSVehicle.HasSharedOrders": "hasSharedOrders",
        "GSVehicle.GetReliability": "reliability",
        "GSVehicle.GetMaximumOrderDistance": "maximum_order_distance",
    }
