from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from libottdadmin2.enums import ChatAction, DestType
from libottdadmin2.packets.server import ServerCompanyInfo


class ChatSchema(Schema):
    action = EnumField(ChatAction, missing=ChatAction.SERVER_MESSAGE)
    type = EnumField(DestType, missing=DestType.BROADCAST)
    client_id = fields.Int(missing=1)
    message = fields.Str()


# class ServerCompanyInfoSchema(AnnotationSchema):
#     class Meta:
#         meta = ServerCompanyInfo.data

chat_schema = ChatSchema()
