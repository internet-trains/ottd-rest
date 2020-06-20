from app.extensions import ma
from app.models.town import Town


class TownSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Town
