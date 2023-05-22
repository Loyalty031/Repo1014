import logging
import bot_api
import bot_right


class Log(object):
    """
    日志管理
    :param file: 日志文件名
    :param level: 日志等级
    """
    __level = logging.WARNING

    def __init__(self, file, level=logging.WARNING):
        logging.basicConfig(filename=fr'.\log\{file}.txt',
                            format='%(asctime)s - %(levelname)s - %(message)s - %(funcName)s',
                            level=level,
                            filemode='a+')

    @staticmethod
    def set_level(level):
        """
        设置日志等级
        :param level: 日志等级
        """
        Log.__level = level

    @staticmethod
    def __send_message_to_dev(message):
        for dev in bot_right.Right().dev_list():
            bot_api.SendPrivateMsg(dev, message)

    def debug(self, msg: str):
        """
        输出debug信息
        :param msg: debug信息
        """
        logging.debug(msg)
        if Log.__level <= logging.DEBUG:
            self.__send_message_to_dev(msg)

    def info(self, msg: str):
        """
        输出info信息
        :param msg: info信息
        """
        logging.info(msg)
        if Log.__level <= logging.INFO:
            self.__send_message_to_dev(msg)

    def warning(self, msg: str):
        """
        输出warning信息
        :param msg: warning信息
        """
        logging.warning(msg)
        if Log.__level <= logging.WARNING:
            self.__send_message_to_dev(msg)

    def error(self, msg: str):
        """
        输出error信息
        :param msg: error信息
        """
        logging.error(msg)
        if Log.__level <= logging.ERROR:
            self.__send_message_to_dev(msg)


log = Log('log')
