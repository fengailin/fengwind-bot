from typing import Optional
from tortoise import fields
from tortoise.models import Model
from ..orm import add_model

add_model("plugins.starrail.srbind_model")

class UserBind(Model):
    __table_args__ = {"extend_existing": True}

    id = fields.IntField(pk=True)
    bot_id = fields.CharField(max_length=64)
    user_id = fields.CharField(max_length=64)
    sr_uid = fields.CharField(max_length=64)
    mys_id = fields.CharField(max_length=64, null=True)
    device_id = fields.CharField(max_length=64, null=True)
    device_fp = fields.CharField(max_length=64, null=True)
    cookie = fields.TextField(null=True)
    stoken = fields.TextField(null=True)

    class Meta:
        table = "sr_user_bind"
