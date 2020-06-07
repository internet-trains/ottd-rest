from app import ma
from app.models.vehicle import Vehicle


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
