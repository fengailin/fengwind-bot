from typing import Any, List, Dict
from tortoise import fields, models
from pydantic import Field, BaseModel
from ..orm import add_model
add_model("plugins.starrail.srgacha_model")
class GachaLogItem(BaseModel):
    id: str
    gacha_id: str
    gacha_type: str
    item_type: str
    item_id: str
    rank_type: str
    name: str
    count: str
    time: str


class GachaLogData(BaseModel):
    size: str
    list_: List[GachaLogItem] = Field(alias="list", default_factory=list)


class GachaLogResponse(BaseModel):
    retcode: int
    message: str
    data: GachaLogData


class GachaLog(BaseModel):
    common: Dict[str, GachaLogItem] = {}
    """
    Stellar Warp
    """
    beginner: Dict[str, GachaLogItem] = {}
    """
    Departure Warp
    """
    character_event: Dict[str, GachaLogItem] = {}
    """
    Character Event Warp
    """
    light_cone_event: Dict[str, GachaLogItem] = {}
    """
    Light Cone Event Warp
    """


class UserGachaLog(models.Model):
    id = fields.IntField(pk=True)
    bot_id = fields.CharField(max_length=64)
    user_id = fields.CharField(max_length=64)
    sr_uid = fields.CharField(max_length=64)
    gacha = fields.JSONField()
    """
    JSON of GachaLog
    """

    class Meta:
        table = "sr_user_gacha_log"
        table_description = "用户的抽卡日志"
