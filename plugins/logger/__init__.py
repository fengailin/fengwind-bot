import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import on_command
from ..database import execute_sql
import inspect
import os,sys
from .utils import logger
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='日志',
    description='加载或保存插件所需设置',
    usage='',
    extra={'prefix':'核心','version': '1.0.4'}
)
import asyncio
from .model import PluginLog


async def log_exception(exception: str):
    try:
        # 获取调用者的模块信息
        current_frame = inspect.currentframe()
        caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
        plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
        logger.opt(colors=True).error(f"<c><u>{plugin_name}</u></c> | {exception}")
        exception = exception.replace("'", "").replace('"', '')
        exception = exception.replace("<", "\\<").replace(">", "\\>")
        sql = "INSERT INTO logs_exception (plugin_name, exception) VALUES ('%s', '%s')" % (plugin_name, exception)
        execute_sql(sql)
    except Exception as e:
        logger.opt(colors=True).error(f"记录插件异常出错: {e}")

async def log_user(event:GroupMessageEvent,operation: str):
    try:
        operation = operation.replace("<", "\\<").replace(">", "\\>")
        # 获取调用者的模块信息
        current_frame = inspect.currentframe()
        caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
        plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
        user_id  = event.user_id
        nickname = event.sender.nickname
        group_id = event.group_id
        logger.opt(colors=True).info(f"<c><u>{plugin_name}</u></c> | {nickname}({user_id}) 在 群 {group_id} 进行了 操作\ {operation}")
        operation = operation.replace("'", "").replace('"', '')
        
        sql = "INSERT INTO logs_user (user_id, group_id, operation) VALUES ('%s','%s','%s')" % (user_id, group_id, operation)
        execute_sql(sql)
    except Exception as e:
        logger.opt(colors=True).error(f"记录用户日志出错: {e}")
async def log_plugin(operation: str):
    try:
        # 获取调用者的模块信息
        current_frame = inspect.currentframe()
        caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
        plugin_name1 = os.path.basename(os.path.dirname(caller_module.__file__))
        operation1 = operation.replace("<", "\\<").replace(">", "\\>")
        logger.opt(colors=True).info(f"<c><u>{plugin_name1}</u></c> | {operation}")
        PluginLog.update_or_create(plugin_name=plugin_name1,operation=operation1)
        sql = "INSERT INTO logs_plugin (plugin_name, operation) VALUES ('%s', '%s')" % (plugin_name1,operation1)
        execute_sql(sql)
    except Exception as e:
        logger.opt(colors=True).error(f"记录插件日志出错: {e}")
async def klog_plugin(operation: str):
    try:
        # 获取调用者的模块信息
        current_frame = inspect.currentframe()
        caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
        plugin_name1 = os.path.basename(os.path.dirname(caller_module.__file__))
        operation1 = operation.replace("<", "\\<").replace(">", "\\>")
        logger.opt(colors=True).info(f"<c><u>{plugin_name1}</u></c> | {operation}")
        await PluginLog.update_or_create(plugin_name=plugin_name1,operation=operation1)
        sql = "INSERT INTO logs_plugin (plugin_name, operation) VALUES ('%s', '%s')" % (plugin_name1,operation1)
        execute_sql(sql)
    except Exception as e:
        logger.opt(colors=True).error(f"记录插件日志出错: {e}")
def log_info(operation: str):
    operation = operation.replace("<", "\\<").replace(">", "\\>")
        # 获取调用者的模块信息
    current_frame = inspect.currentframe()
    caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
    plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
    logger.opt(colors=True).info(f"<c><u>{plugin_name}</u></c> | {operation}")
    
async def log_warning(operation: str):
    operation = operation.replace("<", "\\<").replace(">", "\\>")
        # 获取调用者的模块信息
    current_frame = inspect.currentframe()
    caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
    plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
    logger.opt(colors=True).warning(f"<c><u>{plugin_name}</u></c> | {operation}")