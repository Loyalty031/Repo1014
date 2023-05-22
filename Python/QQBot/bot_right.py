"""
bot_right.py

有关权限的操作
"""
import bot_db
from bot_log import log
from bot_config import config


class Right(object):
    """
    权限管理
    """
    __DEV = 4
    __TEST = 2
    __USER = 1

    def __init__(self):
        self.db = bot_db.DataBase(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            db='bot'
        )

    def __del__(self):
        del self.db

    @property
    def dev(self):
        """
        获取开发者权限
        :return: 开发者权限
        """
        return self.__DEV

    @property
    def test(self):
        """
        获取测试者权限
        :return: 测试者权限
        """
        return self.__TEST

    @property
    def user(self):
        """
        获取用户权限
        :return: 用户权限
        """
        return self.__USER

    @staticmethod
    def is_valid(right):
        """
        判断是否具有有效权限
        :param right: 权限值
        :return: 是否是有效权限
        """
        return right == Right.__USER or right == Right.__TEST or right == Right.__DEV

    @staticmethod
    def is_dev(right):
        """
        判断是否具有开发者权限
        :param right: 权限值
        :return: 是否具有开发者权限
        """
        return right >= Right.__DEV

    @staticmethod
    def is_test(right):
        """
        判断是否具有测试者权限
        :param right: 权限值
        :return: 是否具有测试者权限
        """
        return right >= Right.__TEST

    @staticmethod
    def is_user(right):
        """
        判断是否具有用户权限
        :param right: 权限值
        :return: 是否具有用户权限
        """
        return right >= Right.__USER

    @staticmethod
    def has_right(right, require):
        """
        判断是否具有权限
        :param right: 权限值
        :param require: 要求的权限
        :return: 是否具有权限
        """
        return right >= require

    def get_right(self, user_id: int, group_id: int = 0) -> int:
        """
        获取用户权限
        :param user_id: 用户QQ号
        :param group_id: 群号
        :return: 用户权限
        """
        try:
            if group_id:
                group_right = self.db.execute(f'SELECT `right` FROM `right` WHERE group_id={group_id}')
                return group_right[0][0]
            user_right = self.db.execute(f'SELECT `right` FROM `right` WHERE user_id={user_id}')
            if len(user_right) == 0:
                return 0
            return user_right[0][0]
        except Exception as err:
            log.warning(str(err) + '，获取用户权限失败：user_id=' + str(user_id) + ' group_id=' + str(group_id))
            return 0

    def set_right(self, right: int, user_id: int = 0, group_id: int = 0) -> bool:
        """
        设置用户权限, user_id和group_id至少有一个不为0, 同时不为0时忽略group_id
        :param right: 权限值
        :param user_id: 用户QQ号
        :param group_id: 群号
        :return: 是否设置成功
        """
        try:
            if not self.is_valid(right):
                return False
            # 先查询是否存在, 存在则更新, 不存在则插入
            if user_id:
                if len(self.db.execute(f'SELECT * FROM `right` WHERE user_id={user_id}')) == 0:
                    self.db.execute(f'INSERT INTO `right` VALUES ({user_id}, null, {right})')
                else:
                    self.db.execute(f'UPDATE `right` SET `right`={right} WHERE user_id={user_id}')
            elif group_id:
                if len(self.db.execute(f'SELECT * FROM `right` WHERE group_id={group_id}')) == 0:
                    self.db.execute(f'INSERT INTO `right` VALUES (null, {group_id}, {right})')
                else:
                    self.db.execute(f'UPDATE `right` SET `right`={right} WHERE group_id={group_id}')
            return True
        except Exception as err:
            log.warning(str(err) + '，设置用户权限失败：right=' + str(right) + ' user_id=' + str(user_id) + ' group_id=' +
                        str(group_id))
            return False

    def del_right(self, user_id: int = 0, group_id: int = 0) -> bool:
        """
        删除用户权限, user_id和group_id至少有一个不为0, 同时不为0时忽略group_id
        :param user_id: 用户QQ号
        :param group_id: 群号
        :return: 是否删除成功
        """
        try:
            if user_id:
                self.db.execute(f'DELETE FROM `right` WHERE user_id={user_id}')
            elif group_id:
                self.db.execute(f'DELETE FROM `right` WHERE group_id={group_id}')
            return True
        except Exception as err:
            log.warning(str(err) + '，删除用户权限失败：user_id=' + str(user_id) + ' group_id=' + str(group_id))
            return False

    def dev_list(self) -> tuple:
        """
        获取开发者列表
        :return: 开发者元组
        """
        try:
            raw = self.db.execute(f'SELECT user_id FROM `right` WHERE `right`>={Right.__DEV}')
            return tuple(data[0] for data in raw)
        except bot_db.pymysql.MySQLError:
            return ()

    def test_list(self) -> tuple:
        """
        获取测试者列表
        :return: 测试者元组
        """
        try:
            raw = self.db.execute(f'SELECT user_id FROM `right` WHERE `right`>={Right.__TEST}')
            return tuple(data[0] for data in raw)
        except bot_db.pymysql.MySQLError:
            return ()

    def user_list(self) -> tuple:
        """
        获取用户列表
        :return: 用户元组
        """
        try:
            raw = self.db.execute(f'SELECT user_id FROM `right` WHERE `right`>={Right.__USER}')
            return tuple(data[0] for data in raw)
        except bot_db.pymysql.MySQLError:
            return ()
