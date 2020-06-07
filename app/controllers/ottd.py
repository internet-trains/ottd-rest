from libottdadmin2.client.tracking import TrackingMixIn
from libottdadmin2.enums import UpdateType, UpdateFrequency
from libottdadmin2.client.sync import OttdSocket, DefaultSelector
from libottdadmin2.packets.admin import (
    AdminPoll,
    AdminUpdateFrequency,
    PollExtra,
    AdminGamescript,
)

from logging import warning
from app import db
from config import config
from app.models.town import Town
from app.models.vehicle import Vehicle
from app.controllers.town import TownController
from app.controllers.vehicle import VehicleController
from app.models.company import Company

host = config.OTTD_GS_HOST
port = config.OTTD_GS_PORT
password = config.OTTD_GS_PASSWORD


class Client(TrackingMixIn, OttdSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mailbox = {}
        self.mailbox_iterator = 0
        self.packets_to_send = []

    def get_mailbox(self):
        if self.mailbox_iterator >= 10000:
            self.mailbox_iterator = 0
        self.mailbox_iterator += 1
        self.mailbox[self.mailbox_iterator] = {}
        return self.mailbox_iterator

    def send_packets(self):
        for packet in self.packets_to_send:
            self.send_packet(packet)

        self.packets_to_send = []

    def on_server_gamescript_raw(self, packet, data):
        mailbox_id = data.json_data["number"]
        if mailbox_id in self.mailbox:
            self.mailbox[mailbox_id]["result"] = data.json_data["result"]
            self.mailbox[mailbox_id]["db_synced"] = False
        else:
            warning(f"Message with unknown mailbox_id{mailbox_id}")

    def send_admin_gamescript(self, method, args=[], action="call", company_mode=None):
        mailbox_id = self.get_mailbox()
        data = {"action": action, "method": method, "args": args, "number": mailbox_id}
        if company_mode is not None:
            data["company_mode"] = company_mode

        packet = AdminGamescript.create(json_data=data)
        self.packets_to_send.append(packet)
        self.mailbox[mailbox_id] = {"data": data}
        return mailbox_id


class OpenTTDConnection:
    def __init__(self):
        self.client = Client(password=password)
        self.client.connect((host, port))
        self.selector = DefaultSelector()
        self.client.setblocking(False)
        self.client.register_to_selector(self.selector)
        self.client.send_packet(
            AdminUpdateFrequency.create(
                type=UpdateType.COMPANY_ECONOMY, freq=UpdateFrequency.POLL
            )
        )
        self.client.send_packet(
            AdminUpdateFrequency.create(
                type=UpdateType.GAMESCRIPT, freq=UpdateFrequency.AUTOMATIC
            )
        )
        self.city_cursor = 0
        self.city_scanning = False

    def req_data(self):
        poll_packet = AdminPoll.create(
            type=UpdateType.COMPANY_ECONOMY, extra=PollExtra.ALL
        )
        self.client.send_packet(poll_packet)
        self.client.send_packets()

        self.packets_to_send = []

    def sync_data(self):
        events = self.selector.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

        # sync companies
        # print(self.client.companies)
        for c_id, company in self.client.companies.items():
            company_model = Company.query.get(c_id)
            if company_model is None:
                company_model = Company(id=c_id)

            company_model.name = company.name
            company_model.manager = company.manager
            company_model.color = company.colour
            company_model.passworded = company.passworded
            company_model.start_year = company.startyear
            company_model.is_ai = company.is_ai
            company_model.bankruptcy_counter = company.bankruptcy_counter

            db.session.add(company_model)

        # sync company stats
        for c_id, company_stats in self.client.company_stats.items():
            company_model = Company.query.get(c_id)
            if company_model is None:
                company_model = Company(id=c_id)

            company_model.num_train = company_stats.vehicles.train
            company_model.num_lorry = company_stats.vehicles.lorry
            company_model.num_plane = company_stats.vehicles.plane
            company_model.num_ship = company_stats.vehicles.ship

            company_model.num_train_stations = company_stats.stations.train
            company_model.num_lorry_stations = company_stats.stations.lorry
            company_model.num_plane_stations = company_stats.stations.plane
            company_model.num_ship_stations = company_stats.stations.ship

            db.session.add(company_model)

        # sync company economy
        for c_id, company_economy in self.client.economy.items():
            company_model = Company.query.get(c_id)
            if company_model is None:
                company_model = Company(id=c_id)

            company_model.money = company_economy.money
            company_model.current_loan = company_economy.current_loan
            company_model.income = company_economy.income
            company_model.delivered = company_economy.delivered

            db.session.add(company_model)

        towns_to_update = []
        trigger_new_city_scan_batch = False

        for mb_id, mailbox in self.client.mailbox.items():
            if "db_synced" in mailbox:
                if not mailbox["db_synced"]:
                    method = mailbox["data"]["method"]
                    if method.startswith("GSVehicle"):
                        VehicleController.create_or_update_from_mailbox(
                            mailbox["data"]["args"][0],
                            mailbox,
                            self.client.current_date,
                        )
                    if method.startswith("GSTown"):
                        if method == "GSTown.IsValidTown":
                            if mailbox["result"]:
                                towns_to_update += [mailbox["data"]["args"][0]]
                            if mailbox["data"]["args"][0] == self.city_cursor:
                                if mailbox["result"] == False:
                                    self.city_scanning = False
                                else:
                                    trigger_new_city_scan_batch = True

                        else:
                            TownController.create_or_update_from_mailbox(
                                mailbox["data"]["args"][0],
                                mailbox,
                                self.client.current_date,
                            )
                    mailbox["db_synced"] = True

        # Schedule
        if trigger_new_city_scan_batch:
            self.schedule_next_town_scan_batch(self.city_cursor)

        for town in towns_to_update:
            self.get_town_details(town)

        db.session.commit()

        return self.client.current_date.date

    def add_packet(self, packet):
        self.packets_to_send.append(packet)

    def get_mailbox(self, mailbox_id):
        return self.client.mailbox.get(mailbox_id, None)

    def get_vehicle_details(self, vehicle_id):
        mailbox_ids = []
        vehicle_commands = Vehicle.gs_map.keys()
        for command in vehicle_commands:
            mailbox_ids += [
                self.client.send_admin_gamescript(command, args=[vehicle_id])
            ]

        return mailbox_ids

    #
    # def scan_vehicles(self, max_id=2000):
    #     for v_id in range(max_id):
    #         self.client.send_admin_gamescript("GSVehicle.IsValidVehicle", args=[v_id])

    def schedule_next_town_scan_batch(self, start, batch_size=10):
        for t_id in range(start, start + batch_size):
            self.client.send_admin_gamescript("GSTown.IsValidTown", args=[t_id])
        self.city_cursor = start + batch_size - 1

    def get_town_details(self, town_id):
        mailbox_ids = []
        town_commands = Town.gs_map.keys()
        for command in town_commands:
            mailbox_ids += [self.client.send_admin_gamescript(command, args=[town_id])]

        return mailbox_ids

    def refresh_db_towns(self):
        mailbox_ids = []
        towns = Town.query.all()
        for town in towns:
            mailbox_ids += self.get_town_details(town.id)

        return mailbox_ids

    def refresh_db_vehicles(self):
        mailbox_ids = []
        vehicles = Vehicle.query.all()
        for vehicle in vehicles:
            mailbox_ids += self.get_vehicle_details(vehicle.id)

        return mailbox_ids
