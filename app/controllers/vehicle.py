from datetime import date

from app.models.vehicle import Vehicle
from app import db


class VehicleTimescaleController:
    @classmethod
    def capture_data(cls, current_date):
        if not current_date or current_date < date(1000, 1, 1):
            return

        vehicles = Vehicle.query.all()
        for vehicle in vehicles:
            last_ts = (
                vehicle.timescale_type()
                .query.filter_by(vehicle_id=vehicle.id)
                .order_by(vehicle.timescale_type.timestamp.desc())
                .first()
            )

            matching = True
            new_ts_item = cls.gen_ts_item(vehicle, timestamp=current_date)

            if last_ts:
                if last_ts.timestamp.date() > current_date:
                    old_data = (
                        vehicle.timescale_type.query.filter_by(vehicle_id=vehicle.id)
                        .filter(vehicle.timescale_type.timestamp > current_date)
                        .all()
                    )
                    for data in old_data:
                        db.session.delete(data)
                db.session.commit()

                if last_ts.timestamp.date() == current_date:
                    return

                # TODO: Capture year end data
                for column in Vehicle.timescale_table_value_columns:
                    if getattr(last_ts, column) != getattr(new_ts_item, column):
                        matching = False
            else:
                matching = False

            if not matching:
                db.session.add(new_ts_item)

            db.session.commit()

    @classmethod
    def gen_ts_item(cls, vehicle, timestamp):
        return Vehicle.timescale_type(
            vehicle_id=vehicle.id,
            timestamp=timestamp,
            **{
                column: getattr(vehicle, column)
                for column in Vehicle.timescale_table_value_columns
            }
        )


class VehicleController:
    @classmethod
    def create_or_update_from_mailbox(cls, vehicle_id, mailbox, current_time):
        vehicle = Vehicle.query.filter(Vehicle.id == vehicle_id).first()

        if vehicle is None:
            vehicle = Vehicle(id=vehicle_id)
            db.session.add(vehicle)

        method = mailbox["data"]["method"]
        if method in Vehicle.gs_map.keys():
            setattr(vehicle, Vehicle.gs_map[method], mailbox["result"])

        vehicle.last_updated = current_time

        db.session.commit()

    @classmethod
    def update_by_id(cls, ottd_connection, vehicle_id):
        ottd_connection.get_vehicle_details(vehicle_id)
