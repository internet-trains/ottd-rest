from app.extensions import ma
from app.models.vehicle import Vehicle

from app.schemas.company import CompanySchema

class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        exclude = ('asc_timescale_frames',)
        include_relationships = True