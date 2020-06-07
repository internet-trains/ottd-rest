from datetime import date

from app.models.town import Town
from app import db


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
