from nonebot.adapters.onebot.v11 import GroupMessageEvent
import inspect
import os,sys
from .utils import logger
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='日志',
    description='记录各种有的没的的日志',
    usage='',
    extra={'prefix':'核心','version': '1.1.0-20240629'}
)

from .model import PluginLog,UserLog,ExceptionLog


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

        await ExceptionLog.update_or_create(plugin_name=plugin_name,exception=exception)
        # 写入数据库

        #sql = "INSERT INTO logs_exception (plugin_name, exception) VALUES ('%s', '%s')" % (plugin_name, exception)
        #execute_sql(sql)
        # 陈年屎山，注释掉，说不定之后还要用
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

        await UserLog.update_or_create(user_id=user_id,group_id=group_id,operation=operation)
        # 写入数据库

        #sql = "INSERT INTO logs_user (user_id, group_id, operation) VALUES ('%s','%s','%s')" % (user_id, group_id, operation)
        #execute_sql(sql)
        # 陈年屎山，注释掉，说不定之后还要用
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

        await PluginLog.update_or_create(plugin_name=plugin_name1,operation=operation1)
        # 写入数据库

        #sql = "INSERT INTO logs_plugin (plugin_name, operation) VALUES ('%s', '%s')" % (plugin_name1,operation1)
        #execute_sql(sql)
        # 陈年屎山，注释掉，说不定之后还要用
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