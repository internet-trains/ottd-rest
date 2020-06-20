from app.extensions import db
from app.models.timescale_mixin import TimeScaleMixin


class Town(db.Model, TimeScaleMixin):
    timescale_table_value_columns = ["population", "house_count", "growth_rate"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return f"<Town#{self.id} [{self.name}]>"

    population = db.Column(db.Integer)
    house_count = db.Column(db.Integer)
    location = db.Column(db.Integer)
    growth_rate = db.Column(db.Integer)
    is_city = db.Column(db.Boolean)
    last_updated = db.Column(db.Date)

    gs_map = {
        # ["GetTownCount", GSTown.GetTownCount, ""],
        # "GSTown.IsValidTown": 'is_valid_town',
        "GSTown.GetName": "name",
        # ["SetName", GSTown.SetName, "i."],
        # ["SetText", GSTown.SetText, "i."],
        "GSTown.GetPopulation": "population",
        "GSTown.GetHouseCount": "house_count",
        "GSTown.GetLocation": "location",
        # ["GetLastMonthProduction", GSTown.GetLastMonthProduction, "ii"],
        # ["GetLastMonthSupplied", GSTown.GetLastMonthSupplied, "ii"],
        # ["GetLastMonthTransportedPercentage", GSTown.GetLastMonthTransportedPercentage, "ii"],
        # ["GetLastMonthReceived", GSTown.GetLastMonthReceived, "ii"],
        # ["SetCargoGoal", GSTown.SetCargoGoal, "iii"],
        # ["GetCargoGoal", GSTown.GetCargoGoal, "ii"],
        # ["SetGrowthRate", GSTown.SetGrowthRate, "ii"],
        "GSTown.GetGrowthRate": "growth_rate",
        # ["GetDistanceManhattanToTile", GSTown.GetDistanceManhattanToTile, "ii"],
        # ["GetDistanceSquareToTile", GSTown.GetDistanceSquareToTile, "ii"],
        # ["IsWithinTownInfluence", GSTown.IsWithinTownInfluence, "ii"],
        # ["HasStatue", GSTown.HasStatue, "i"],
        "GSTown.IsCity": "is_city",
        # ["GetRoadReworkDuration", GSTown.GetRoadReworkDuration, "i"],
        # ["GetFundBuildingsDuration", GSTown.GetFundBuildingsDuration, "i"],
        # ["GetExclusiveRightsCompany", GSTown.GetExclusiveRightsCompany, "i"],
        # ["GetExclusiveRightsDuration", GSTown.GetExclusiveRightsDuration, "i"],
        # ["IsActionAvailable", GSTown.IsActionAvailable, "ii"],
        # ["PerformTownAction", GSTown.PerformTownAction, "ii"],
        # ["ExpandTown", GSTown.ExpandTown, "ii"],
        # ["FoundTown", GSTown.FoundTown, "iibi."],
        # ["GetRating", GSTown.GetRating, "ii"],
        # ["GetDetailedRating", GSTown.GetDetailedRating, "ii"],
        # ["ChangeRating", GSTown.ChangeRating, "iii"],
        # ["GetAllowedNoise", GSTown.GetAllowedNoise, "i"],
        # ["GetRoadLayout", GSTown.GetRoadLayout, "i"],
    }
