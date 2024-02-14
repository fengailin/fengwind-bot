import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import on_command
from ..database import execute_sql
import inspect
import os,sys

__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name='日志',
    description='加载或保存插件所需设置',
    usage='',
    extra={'prefix':'核心','version': '1.0.4'}
)



import loguru

logger = loguru.logger

default_format: str = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    #"<c><u>{module}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}"
)
"""默认日志格式"""
def default_filter(record):
    """默认的日志过滤器，根据 `config.log_level` 配置改变日志等级。"""
    log_level = record["extra"].get("nonebot_log_level", "INFO")
    levelno = logger.level(log_level).no if isinstance(log_level, str) else log_level
    return record["level"].no >= levelno

logger.remove()
logger_id = logger.add(
    sys.stdout,
    level=0,
    diagnose=False,
    filter=default_filter,
    format=default_format,

)


def log_exception(exception: str):
    try:
        # 获取调用者的模块信息
        current_frame = inspect.currentframe()
        caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
        plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
        logger.opt(colors=True).error(f"<c><u>{plugin_name}</u></c> | {exception}")
        exception = exception.replace("'", "").replace('"', '')
        sql = "INSERT INTO logs_exception (plugin_name, exception) VALUES ('%s', '%s')" % (plugin_name, exception)
        execute_sql(sql)
    except Exception as e:
        logger.opt(colors=True).error(f"记录插件异常出错: {e}")

def log_user(event:GroupMessageEvent,operation: str):
    try:
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
def log_plugin(operation: str):
    try:
        # 获取调用者的模块信息
        current_frame = inspect.currentframe()
        caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
        plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
        logger.opt(colors=True).info(f"<c><u>{plugin_name}</u></c> | {operation}")
        operation = operation.replace("'", "").replace('"', '')
        sql = "INSERT INTO logs_plugin (plugin_name, operation) VALUES ('%s', '%s')" % (plugin_name,operation)
        execute_sql(sql)
    except Exception as e:
        logger.opt(colors=True).error(f"记录插件日志出错: {e}")
def log_info(operation: str):
        # 获取调用者的模块信息
    current_frame = inspect.currentframe()
    caller_module = inspect.getmodule(current_frame.f_back)
        
        # 从模块信息中获取插件名
    plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
    
    logger.opt(colors=True).info(f"<c><u>{plugin_name}</u></c> | {operation}")