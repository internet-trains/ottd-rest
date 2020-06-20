from datetime import date

from app.models.town import Town
from app.extensions import db


class TownController:
    @classmethod
    def create_or_update_from_mailbox(cls, town_id, mailbox, current_time):
        town = Town.query.filter(Town.id == town_id).first()

        if town is None:
            town = Town(id=town_id)
            db.session.add(town)

        method = mailbox["data"]["method"]
        if method in Town.gs_map.keys():
            setattr(town, Town.gs_map[method], mailbox["result"])

        town.last_updated = current_time

        db.session.commit()

class TownTimescaleController:
    @classmethod
    def capture_data(cls, current_date):
        if not current_date or current_date < date(1000, 1, 1):
            return

        towns = Town.query.all()
        for town in towns:
            last_ts = (
                town.timescale_type()
                .query.filter_by(town_id=town.id)
                .order_by(town.timescale_type.timestamp.desc())
                .first()
            )

            matching = True
            new_ts_item = cls.gen_ts_item(town, timestamp=current_date)

            if last_ts:
                if last_ts.timestamp.date() > current_date:
                    old_data = (
                        town.timescale_type.query.filter_by(town_id=town.id)
                        .filter(town.timescale_type.timestamp > current_date)
                        .all()
                    )
                    for data in old_data:
                        db.session.delete(data)
                db.session.commit()

                if last_ts.timestamp.date() == current_date:
                    return

                for column in Town.timescale_table_value_columns:
                    if getattr(last_ts, column) != getattr(new_ts_item, column):
                        matching = False
            else:
                matching = False

            if not matching:
                db.session.add(new_ts_item)

            db.session.commit()

    @classmethod
    def gen_ts_item(cls, town, timestamp):
        return Town.timescale_type(
            town_id=town.id,
            timestamp=timestamp,
            **{
                column: getattr(town, column)
                for column in Town.timescale_table_value_columns
            }
        )