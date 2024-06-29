from typing import Any, List, Dict
from tortoise import fields
from tortoise.models import Model
from ..orm import add_model
add_model("plugins.logger.model")

class PluginLog(Model):
    log_id = fields.IntField(pk=True)
    plugin_name = fields.CharField(max_length=255)
    operation = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "log_plugin"
        table_description = "插件日志" # 可选