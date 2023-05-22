import pymysql
from bot_log import log
from bot_config import config


class DataBase(object):
    """
    数据库操作
    :param host: 数据库地址
    :param user: 数据库用户名
    :param password: 数据库密码
    :param db: 数据库名
    """

    def __init__(self, host: str, user: str, password: str, db: str):
        if config['database']['available']:
            self.db_connect = pymysql.connect(host=host, user=user, password=password, database=db)
            self.cursor = self.db_connect.cursor()

    def __del__(self):
        if config['database']['available']:
            self.cursor.close()
            self.db_connect.close()

    def execute(self, cmd: str) -> tuple[tuple[..., ...], ...]:
        """
        执行MySQL语句
        :param cmd: MySQL语句
        :return: MySQL语句执行结果
        """
        if config['database']['available']:
            try:
                self.cursor.execute(cmd)
                self.db_connect.commit()
                log.info('执行MySQL语句成功：' + cmd)
                return self.cursor.fetchall()
            except pymysql.MySQLError as err:
                self.db_connect.rollback()
                log.warning(str(err) + '，执行MySQL语句失败：' + cmd)
                return ()
