from app import ma
from app.models.company import Company


class CompanySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Company
