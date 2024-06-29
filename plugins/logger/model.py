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


class UserLog(Model):
    log_id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=255)
    group_id = fields.CharField(max_length=255)
    operation = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "log_user"
        table_description = "用户日志" # 可选

class ExceptionLog(Model):
    log_id = fields.IntField(pk=True)
    plugin_name = fields.CharField(max_length=255)
    exception = fields.TextField()
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "log_exception"
        table_description = "异常日志" # 可选