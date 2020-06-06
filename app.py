# from flask import Flask, escape, request
from quart import Quart, websocket, request, jsonify
from quart.json import loads

import argparse
import asyncio
import logging

from flask_smorest import Api, Blueprint, abort
from flask_sqlalchemy import SQLAlchemy
from libottdadmin2.client.tracking import TrackingMixIn
from libottdadmin2.client.asyncio import OttdAdminProtocol
from libottdadmin2.constants import NETWORK_ADMIN_PORT
from libottdadmin2.enums import ChatAction, DestType, UpdateType, UpdateFrequency
from libottdadmin2.packets.admin import (
    AdminChat,
    AdminPoll,
    AdminUpdateFrequency,
    PollExtra,
    AdminGamescript,
)
from libottdadmin2.packets import Packet

from schemas import chat_schema


host = "127.0.0.1"
port = NETWORK_ADMIN_PORT
password = "password"

app = Quart("OpenTTD REST Server")
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

db = SQLAlchemy(app)
api = Api(app)

logging.basicConfig(level=logging.DEBUG)


class Client(TrackingMixIn, OttdAdminProtocol):
    pass


async def server_poll(timeout):
    while True:
        await asyncio.sleep(timeout)
        poll_packet = AdminPoll.create(
            type=UpdateType.COMPANY_ECONOMY, extra=PollExtra.ALL
        )
        app.ottd_client.send_packet(poll_packet)


@app.before_serving
async def b4_1st_req():
    loop = asyncio.get_event_loop()
    app.ottd_client = await Client.connect(
        loop=loop, host=host, port=port, password=password
    )
    app.polling_task = asyncio.create_task(server_poll(timeout=1))
    # get loaded gs, check for admin bindings app.ottd_client
    app.ottd_client.send_packet(
        AdminUpdateFrequency.create(
            type=UpdateType.COMPANY_ECONOMY, freq=UpdateFrequency.POLL
        )
    )
    app.ottd_client.send_packet(
        AdminUpdateFrequency.create(
            type=UpdateType.GAMESCRIPT, freq=UpdateFrequency.AUTOMATIC
        )
    )


@app.route("/chat", methods=["PUT"])
async def chat():
    r = await request.get_data()
    req_dict = loads(r)
    chat_packet = AdminChat.create(**chat_schema.load(req_dict))
    app.ottd_client.send_packet(chat_packet)
    return jsonify({})


@app.route("/companies", methods=["GET"])
async def list_companies():
    companies = list(app.ottd_client.companies.values())
    obj_repr = list(map(lambda company: company._asdict(), companies))
    return jsonify(obj_repr)


@app.route("/all_economies", methods=["GET"])
async def all_economies():
    economies = list(app.ottd_client.economy.values())
    obj_repr = list(map(lambda economy: economy._asdict(), economies))
    return jsonify(obj_repr)


@app.route("/time", methods=["GET"])
async def the_time():
    return jsonify(app.ottd_client.current_date)


@app.route("/list_cmds", methods=["GET"])
async def list_cmds():
    for key, value in app.ottd_client.commands.items():
        print(key, value)

    return "ok"


@app.route("/company/<int:company_id>/change", methods=["POST"])
async def change_company_name(company_id):
    packet = AdminGamescript.create(
        json_data={
            "action": "call",
            "method": "  GSVehicleList",
            # "args": [0, "'adman'"]
        }
    )
    app.ottd_client.send_packet(packet)
    return "ok"


@app.route("/")
async def hello():
    return "hello"


@app.route("/vechicle/<int:vehicle_id>/", methods=["GET"])
async def vehicle(vehicle_id):
    return ""


@app.websocket("/ws")
async def ws():
    while True:
        await websocket.send("hello")


app.run()
