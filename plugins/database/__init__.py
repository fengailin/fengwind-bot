import pymysql
from ..config import config_data
#from ..Utils import plugin_log
from pymysql import cursors
import nonebot
import datetime
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='数据库',
    description='提供数据库连接',
    usage='',
    extra={'prefix': '核心', 'version': '1'}
)


host = config_data['mysql']['host']
user = config_data['mysql']['user']
password = config_data['mysql']['password']
database = config_data['mysql']['database']

mysql = pymysql.connect(host=host,
                         user=user,
                         password=password,
                         database=database,
                         charset='utf8',
                         autocommit=True,
                         cursorclass=cursors.SSDictCursor)

mysql = pymysql.connect(host=host,
                        #port=port,
                        user=user,
                        password=password,
                        database=database,
                        charset='utf8',
                        autocommit=True,
                        cursorclass=cursors.SSDictCursor)


def execute_sql(sqlcontent):
    """
    sql执行函数
    :param sqlcontent: 需要执行的sql语句
    :return: sql执行结果
    """
    try:
        
        cursor = mysql.cursor()
        mysql.ping(reconnect=True)
        cursor.execute(sqlcontent)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        nonebot.logger.error(f"数据库出错: {e}")
#        plugin_log(__plugin_name__, str(e), levelname="ERROR")
        return []