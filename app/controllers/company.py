from datetime import datetime, date
from app import db
from app.models.company import Company


class CompanyTimescaleController:
    @classmethod
    def capture_data(cls, current_date):
        if not current_date or current_date < date(1000, 1, 1):
            return

        companies = Company.query.all()
        for company in companies:
            if company.id == 255:
                # don't store stats for spectator
                continue

            last_ts = (
                company.timescale_type()
                .query.filter_by(company_id=company.id)
                .order_by(company.timescale_type.timestamp.desc())
                .first()
            )

            if last_ts:
                if last_ts.timestamp.date() > current_date:
                    old_data = (
                        company.timescale_type.query.filter_by(company_id=company.id)
                        .filter(company.timescale_type.timestamp > current_date)
                        .all()
                    )
                    for data in old_data:
                        db.session.delete(data)
                db.session.commit()

                if last_ts.timestamp.date() == current_date:
                    return

                # Capture year end data we may have missed
                if last_ts and last_ts.delivered < company.delivered:
                    cls.create_year_end_data(last_ts, company, current_date)

            new_ts_item = cls.gen_ts_item(company, timestamp=current_date)
            db.session.add(new_ts_item)
            db.session.commit()

    @classmethod
    def gen_ts_item(cls, company, timestamp):
        return Company.timescale_type(
            company_id=company.id,
            timestamp=timestamp,
            ## Train Counts
            num_train=company.num_train,
            num_lorry=company.num_lorry,
            num_plane=company.num_plane,
            num_ship=company.num_ship,
            ## Station Counts
            num_train_stations=company.num_train_stations,
            num_lorry_stations=company.num_lorry_stations,
            num_plane_stations=company.num_plane_stations,
            num_ship_stations=company.num_ship_stations,
            ## Economy Data
            money=company.money,
            current_loan=company.current_loan,
            income=company.income,
            delivered=company.delivered,
        )

    @classmethod
    def create_year_end_data(cls, prev_ts, company, current_date: datetime):
        last_year = current_date.year - 1
        last_date = datetime(last_year, 12, 31, 11, 59, 59)
        ts_item = cls.gen_ts_item(company, last_date)  # noqa

        # TODO: Derive numbers from ServerEconomyHistoryValue
