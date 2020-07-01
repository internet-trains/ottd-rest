from marshmallow import fields

from app.extensions import ma
from app.models.town import Town


class TownSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Town

class TownGrowSchema(ma.Schema):
    houses = fields.Int(description="Number of houses you wish to grow the town by.")

class TownTextSchema(ma.Schema):
    text = fields.Str(description="Name you wish to set the town text to.")

class TownNameSchema(ma.Schema):
    name = fields.Str(description="Name you wish to set the town's name to.")