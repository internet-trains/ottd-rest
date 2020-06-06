from app import db
from app.models.timescale_mixin import TimeScaleMixin


class Company(db.Model, TimeScaleMixin):
    timescale_table_value_columns = [
        "num_train",
        "num_lorry",
        "num_plane",
        "num_ship",
        "num_train_stations",
        "num_lorry_stations",
        "num_plane_stations",
        "num_ship_stations",
        "money",
        "current_loan",
        "income",
        "delivered",
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    manager = db.Column(db.String(64))
    color = db.Column(db.Integer)
    passworded = db.Column(db.Boolean)
    start_year = db.Column(db.Integer)
    is_ai = db.Column(db.Boolean)
    bankruptcy_counter = db.Column(db.Integer)

    ## Vehicle Counts
    num_train = db.Column(db.Integer, server_default="0")
    num_lorry = db.Column(db.Integer, server_default="0")
    num_plane = db.Column(db.Integer, server_default="0")
    num_ship = db.Column(db.Integer, server_default="0")

    ## Station Counts
    num_train_stations = db.Column(db.Integer, server_default="0")
    num_lorry_stations = db.Column(db.Integer, server_default="0")
    num_plane_stations = db.Column(db.Integer, server_default="0")
    num_ship_stations = db.Column(db.Integer, server_default="0")

    ## Economy Data
    money = db.Column(db.BigInteger, server_default="0")
    current_loan = db.Column(db.BigInteger, server_default="0")
    income = db.Column(db.BigInteger, server_default="0")
    delivered = db.Column(db.BigInteger, server_default="0")

    def __repr__(self):
        return f"<Company#{self.id} [{self.name}]>"
