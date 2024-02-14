import pymysql
from ..config import mysql_config
#from ..Utils import plugin_log
from pymysql import cursors
import nonebot
import datetime

# ChatGPT 作品
__plugin_name__ = '数据库'
__plugin_usage__ = '提供数据库连接'

host = mysql_config['host']
user = mysql_config['user']
password = mysql_config['password']
database = mysql_config['database']

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