from sqlalchemy.ext.declarative import declared_attr

from app.extensions import db, ma
from marshmallow import fields


class TimeScaleMixin:
    @declared_attr
    def _timescale_table_fk_name(cls):
        try:
            return cls.timescale_table_fk_name
        except AttributeError:
            return f"{cls.__tablename__}_id"

    @declared_attr
    def _timescale_table_name(cls):
        try:
            return cls.timescale_table_name
        except AttributeError:
            return f"{cls.__tablename__}_timescale"

    @declared_attr
    def _timescale_table_value_columns(cls):
        try:
            return cls.timescale_table_value_columns
        except AttributeError:
            return ["value"]

    @declared_attr
    def timescale_type(cls):
        class TimeScaleStat(db.Model):
            __table__ = db.Table(
                cls._timescale_table_name,
                db.Column(
                    cls._timescale_table_fk_name,
                    db.Integer,
                    db.ForeignKey(f"{cls.__tablename__}.id"),
                    nullable=False,
                ),
                db.Column("timestamp", db.DateTime, nullable=False),
                db.PrimaryKeyConstraint(cls._timescale_table_fk_name, "timestamp",),
                *(
                    db.Column(
                        column,
                        db.Integer(),
                        default=0,
                        server_default="0",
                        nullable=False,
                    )
                    for column in cls._timescale_table_value_columns
                ),
            )

        return TimeScaleStat

    @declared_attr
    def asc_timescale_frames(cls):
        return db.relationship(cls.timescale_type)

    @classmethod
    def timescale_schema(cls):
        class TimeScaleSchema(ma.SQLAlchemyAutoSchema):
            class Meta:
                model = cls.timescale_type
                include_fk = False

        return type(
            f"{cls.__tablename__.capitalize()}TimeScaleSchema", (TimeScaleSchema,), {}
        )

    def timescale_data_upsert(self, model_id, timestamp, commit=True, **kwargs):
        found_ts = self.timescale_type.query.filter_by(
            getattr(self, self._timescale_table_fk_name) == model_id,
            self.timestamp == timestamp,
        ).first()
        if not found_ts:
            found_ts = self.timescale_type()

        for key, value in kwargs.items():
            setattr(found_ts, key, value)

        db.session.add(found_ts)

        if commit:
            db.session.commit(found_ts)


class TimeScaleRequestSchema(ma.Schema):
    start = fields.Date(description="Start Date")
    end = fields.Date(description="End Date")
    sampling = fields.Str(description="Granularity of data")
