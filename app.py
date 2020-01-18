# from flask import Flask, escape, request
from quart import Quart, websocket, request

app = Quart(__name__)

import argparse
import asyncio
import logging

from libottdadmin2.client.tracking import TrackingMixIn
from libottdadmin2.client.asyncio import OttdAdminProtocol
from libottdadmin2.constants import NETWORK_ADMIN_PORT
from libottdadmin2.enums import ChatAction, DestType
from libottdadmin2.packets.admin import AdminChat
from libottdadmin2.packets import Packet

host = "127.0.0.1"
port = NETWORK_ADMIN_PORT
password = "password"

logging.basicConfig(level=logging.DEBUG)

class Client(TrackingMixIn, OttdAdminProtocol):
    pass

# @app.before_serving
# async def startup():
#     loop = asyncio.get_event_loop()
#     app.smtp_server = loop.create_server(aiosmtpd.smtp.SMTP, port=1025)
#     loop.create_task(app.smtp_server)

# @app.after_serving
# async def shutdown():
#     app.smtp_server.close()


@app.before_serving
async def b4_1st_req():
    loop = asyncio.get_event_loop()
    app.ottd_client = await Client.connect(loop=loop, host=host, port=port, password=password)
    # app.ottd_client_active = await app.ottd_client.client_active  
    # client = loop.run_until_complete(Client.connect(loop=loop, host=host, port=port, password=password))
    # loop.run_until_complete(client.client_active)

@app.route('/chat')
async def chat():
    msg = request.args.get("msg")
    chat_packet = AdminChat.create(**{
        'action': ChatAction.SERVER_MESSAGE, 
        'type': DestType.BROADCAST, 
        'client_id': 1, 
        'message': msg
    })
    # chat_packet = AdminChat.encode(ChatAction.CHAT, type=DestType.BROADCAST, client_id=1, message=msg)
    # chat_packet = 
    app.ottd_client.send_packet(chat_packet)
    return "done."

@app.route('/')
async def hello():
    return 'hello'

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('hello')

app.run()
