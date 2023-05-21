"""
GOCQHTTP的大部分API
https://docs.go-cqhttp.org/api/#api
"""
import requests
import bot_db
from re import sub
from pymysql.converters import escape_string
from bot_config import config


class API(object):
    """
    GOCQHTTP的大部分API
    https://docs.go-cqhttp.org/api/#api
    """
    count: int

    def __init__(self, api: str, data: dict):
        data.pop('self')
        data.pop('__class__')
        self.api = api
        self.data = data
        self.response = requests.post(
            url='http://{}:{}/{}'.format(
                config["go-cqhttp"]["server"]["host"],
                config["go-cqhttp"]["server"]["port"],
                sub(r"(?P<key>[A-Z])", r"_\g<key>", api).lower()[1:]  # 把大驼峰命名的类名转化为小写字母加下划线分隔
            ).encode(),
            json=data
        )
        self.json = self.response.json()

    @classmethod
    def get_count_dict(cls):
        """
        获取每个子类的count计数，返回键值对
        :return: 一个字典，键为子类名，值为count计数
        """
        count_dict = {}
        for sub_cls in cls.__subclasses__():
            count_dict.update({sub_cls.__name__: sub_cls.count})
        return count_dict

    @classmethod
    def get_total_count(cls):
        """
        获取所有子类的count计数总和
        :return: 计数总和
        """
        total = 0
        for sub_cls in cls.__subclasses__():
            total += sub_cls.count
        return total


class BlankApi(API):
    """
    空的API，什么都不做
    """
    count = 0

    def __init__(self):
        BlankApi.count += 1
        super().__init__('', locals())


class Account(API):
    """
    Bot账号
    https://docs.go-cqhttp.org/api/#bot-%E8%B4%A6%E5%8F%B7
    """
    count = 0

    def __init__(self, api: str, data: dict):
        Account.count += 1
        super().__init__(api, data)


class GetLoginInfo(Account):
    """
    获取登录号信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%99%BB%E5%BD%95%E5%8F%B7%E4%BF%A1%E6%81%AF

    响应数据: user_id int64 QQ号, nickname string QQ昵称
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetQqProfile(Account):
    """
    设置登录号资料
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%99%BB%E5%BD%95%E5%8F%B7%E8%B5%84%E6%96%99

    响应数据: 该API无响应数据
    :param nickname: 名称
    :param company: 公司
    :param email: 邮箱
    :param college: 学校
    :param personal_note: 个人说明
    """
    count = 0

    def __init__(self, nickname: str, company: str, email: str, college: str, personal_note: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class _GetModelShow(Account):
    """
    获取在线机型
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E5%9C%A8%E7%BA%BF%E6%9C%BA%E5%9E%8B

    响应数据: variants array, 其中model_show str, need_pay bool
    :param model: 机型名称
    """
    count = 0

    def __init__(self, model: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class _SetModelShow(Account):
    """
    设置在线机型
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E5%9C%A8%E7%BA%BF%E6%9C%BA%E5%9E%8B

    响应数据: 该API无响应数据
    :param model: 机型名称
    :param model_show:
    """
    count = 0

    def __init__(self, model: str, model_show: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetOnlineClients(Account):
    """
    获取当前账号在线客户端列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E5%BD%93%E5%89%8D%E8%B4%A6%E5%8F%B7%E5%9C%A8%E7%BA%BF%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%88%97%E8%A1%A8

    响应数据: clients Device[] 在线客户端列表

    Device: app_id int64 客户端ID device_name str 设备名称 device_kind str 设备类型
    :param: no_cache: 是否无视缓存
    """
    count = 0

    def __init__(self, no_cache: bool):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class FriendInfo(API):
    """
    好友信息
    https://docs.go-cqhttp.org/api/#%E5%A5%BD%E5%8F%8B%E4%BF%A1%E6%81%AF
    """
    count = 0

    def __init__(self, api: str, data: dict):
        FriendInfo.count += 1
        super().__init__(api, data)


class GetStrangerInfo(FriendInfo):
    """
    获取陌生人信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E9%99%8C%E7%94%9F%E4%BA%BA%E4%BF%A1%E6%81%AF

    响应数据: user_id int QQ号, nickname str 昵称, sex str 性别, age int 年龄, qid str qid ID身份卡, level int 等级,
    login_days int 等级
    :param user_id: QQ号
    :param no_cache: 是否不使用缓存（使用缓存可能更新不及时, 但响应更快）
    """
    count = 0

    def __init__(self, user_id: int, no_cache: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetFriendList(FriendInfo):
    """
    获取好友列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E5%A5%BD%E5%8F%8B%E5%88%97%E8%A1%A8

    响应数据: user_id int QQ号,nickname str 昵称,remark str 备注名
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetUnidirectionalFriendList(FriendInfo):
    """
    获取单向好友列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E5%8D%95%E5%90%91%E5%A5%BD%E5%8F%8B%E5%88%97%E8%A1%A8

    响应数据: user_id int QQ号,nickname str 昵称,source str 来源
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class FriendOperation(API):
    """
    好友操作
    https://docs.go-cqhttp.org/api/#%E5%A5%BD%E5%8F%8B%E6%93%8D%E4%BD%9C
    """
    count = 0

    def __init__(self, api: str, data: dict):
        FriendOperation.count += 1
        super().__init__(api, data)


class DeleteFriend(FriendOperation):
    """
    删除好友
    https://docs.go-cqhttp.org/api/#%E5%88%A0%E9%99%A4%E5%A5%BD%E5%8F%8B

    响应数据: 该API无响应数据
    :param user_id: int64,好友QQ号
    """
    count = 0

    def __init__(self, user_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class DeleteUnidirectionalFriend(FriendOperation):
    """
    删除单向好友
    https://docs.go-cqhttp.org/api/#%E5%88%A0%E9%99%A4%E5%8D%95%E5%90%91%E5%A5%BD%E5%8F%8B

    响应数据: 该API无响应数据
    :param user_id: int64,单向好友QQ号
    """
    count = 0

    def __init__(self, user_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class Message(API):
    """
    消息
    https://docs.go-cqhttp.org/api/#%E6%B6%88%E6%81%AF
    """
    count = 0

    def __init__(self, api: str, data: dict):
        Message.count += 1
        super().__init__(api, data)


class SendPrivateMsg(Message):
    """
    发送私聊消息
    https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E7%A7%81%E8%81%8A%E6%B6%88%E6%81%AF

    响应数据: message_id int 消息 ID
    :param user_id: 对方 QQ 号
    :param message: 要发送的内容
    :param group_id: 主动发起临时会话时的来源群号(可选, 机器人本身必须是管理员/群主)
    :param auto_escape: 消息内容是否作为纯文本发送 ( 即不解析 CQ 码 ) , 只在 message 字段是字符串时有效
    """
    count = 0

    def __init__(self, user_id: int, message: str, group_id: int = None, auto_escape: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())
        db = bot_db.DataBase(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            db='bot'
        )
        if group_id is None:
            sql = f'''insert into message
                        (message_id, user_id, message)
                        VALUES
                        ({self.response.json()['data']['message_id']}, {user_id}, '{escape_string(message)}')'''
        else:
            sql = f'''insert into message
                        (message_id, user_id, group_id, message)
                        VALUES
                        ({self.response.json()['data']['message_id']}, {user_id}, {group_id}, '{escape_string(message)}')'''
        db.execute(sql)


class SendGroupMsg(Message):
    """
    发送群聊消息
    https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E7%BE%A4%E8%81%8A%E6%B6%88%E6%81%AF

    响应数据: message_id int 消息 ID
    :param group_id: 群号
    :param message: 要发送的内容
    :param auto_escape: 消息内容是否作为纯文本发送 ( 即不解析 CQ 码 ) , 只在 message 字段是字符串时有效
    """
    count = 0

    def __init__(self, group_id: int, message: str, auto_escape: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())
        db = bot_db.DataBase(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            db='bot'
        )
        db.execute(f'''insert into message 
                (message_id, group_id, message) 
                VALUES 
                ({self.response.json()['data']['message_id']}, {group_id}, '{escape_string(message)}')''')


class SendMsg(Message):
    """
    发送消息
    https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E6%B6%88%E6%81%AF

    响应数据: message_id int 消息 ID
    :param message_type: 消息类型, 支持 private、group , 分别对应私聊、群组, 如不传入, 则根据传入的 *_id 参数判断
    :param user_id: 对方 QQ 号 ( 消息类型为 private 时需要 )
    :param group_id: 群号 ( 消息类型为 group 时需要 )
    :param message: 要发送的内容
    :param auto_escape: 消息内容是否作为纯文本发送 ( 即不解析 CQ 码 ) , 只在 message 字段是字符串时有效
    """
    count = 0

    def __init__(
            self,
            message_type: str, message: str,
            user_id: int = None, group_id: int = None, auto_escape: bool = False
    ):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())
        db = bot_db.DataBase(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            db='bot'
        )
        if group_id is None:
            sql = f'''insert into message 
                (message_id, user_id, message) 
                VALUES 
                ({self.response.json()['data']['message_id']}, {user_id}, '{escape_string(message)}')'''
        else:
            sql = f'''insert into message 
                (message_id, group_id, message) 
                VALUES 
                ({self.response.json()['data']['message_id']}, {group_id}, '{escape_string(message)}')'''
        db.execute(sql)


class GetMsg(Message):
    """
    获取消息 其中sender字段包含: nickname str 发送者昵称 user_id int 发送者 QQ 号
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E6%B6%88%E6%81%AF

    响应数据: group bool 是否是群消息, group_id int 是群消息时的群号(否则不存在此字段), message_id int 消息id, real_id int 消息真实id,
    message_type str 群消息时为group, 私聊消息为private, sender object 发送者, time int 发送时间, message message 消息内容,
    raw_message message 原始消息内容
    :param message_id: 消息id
    """
    count = 0

    def __init__(self, message_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class DeleteMsg(Message):
    """
    撤回消息
    https://docs.go-cqhttp.org/api/#%E6%92%A4%E5%9B%9E%E6%B6%88%E6%81%AF

    响应数据: 该 API 无响应数据
    :param message_id: 消息 ID
    """
    count = 0

    def __init__(self, message_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class MarkMsgAsRead(Message):
    """
    标记消息已读
    https://docs.go-cqhttp.org/api/#%E6%A0%87%E8%AE%B0%E6%B6%88%E6%81%AF%E5%B7%B2%E8%AF%BB

    响应数据: 该 API 无响应数据
    :param message_id: 消息 ID
    """
    count = 0

    def __init__(self, message_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetForwardMsg(Message):
    """
    获取合并转发内容
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91%E5%86%85%E5%AE%B9

    响应数据: messages forward message[] 消息列表
    :param message_id: 消息id
    """
    count = 0

    def __init__(self, message_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SendGroupForwardMsg(Message):
    """
    发送合并转发 ( 群聊 )
    https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91-%E7%BE%A4%E8%81%8A

    CQcode: https://docs.go-cqhttp.org/cqcode/#%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91%E6%B6%88%E6%81%AF%E8%8A%82%E7%82%B9

    响应数据: message_id int 消息 ID, forward_id str 转发消息 ID
    :param group_id: 群号
    :param messages: 自定义转发消息, 具体看 CQcode
    """
    count = 0

    def __init__(self, group_id: int, messages):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SendPrivateForwardMsg(Message):
    """
    发送合并转发 ( 好友 )
    https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91-%E5%A5%BD%E5%8F%8B

    CQcode: https://docs.go-cqhttp.org/cqcode/#%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91%E6%B6%88%E6%81%AF%E8%8A%82%E7%82%B9

    响应数据: message_id int 消息 ID, forward_id str 转发消息 ID
    :param user_id: 好友QQ号
    :param messages: 自定义转发消息, 具体看 CQcode
    """
    count = 0

    def __init__(self, user_id: int, messages):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupMsgHistory(Message):
    """
    获取群消息历史记录
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%B6%88%E6%81%AF%E5%8E%86%E5%8F%B2%E8%AE%B0%E5%BD%95

    响应数据: messages Message[] 从起始序号开始的前19条消息
    :param message_seq: 起始消息序号, 可通过 get_msg 获得, 不提供起始序号将默认获取最新的消息
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int, message_seq: int = None):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class Image(API):
    """
    图片
    https://docs.go-cqhttp.org/api/#%E5%9B%BE%E7%89%87
    """
    count = 0

    def __init__(self, api: str, data: dict):
        Image.count += 1
        super().__init__(api, data)


class GetImage(Image):
    """
    获取图片信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E4%BF%A1%E6%81%AF

    响应数据: size	int32	图片源文件大小, filename	string	图片文件原名, url	string	图片下载地址
    :param file: 图片缓存文件名
    """
    count = 0

    def __init__(self, file: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class CanSendImage(Image):
    """
    检查是否可以发送图片
    https://docs.go-cqhttp.org/api/#%E6%A3%80%E6%9F%A5%E6%98%AF%E5%90%A6%E5%8F%AF%E4%BB%A5%E5%8F%91%E9%80%81%E5%9B%BE%E7%89%87

    响应数据: yes boolean 是或否
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class OcrImage(Image):
    """
    图片 OCR
    https://docs.go-cqhttp.org/api/#%E5%9B%BE%E7%89%87-ocr

    响应数据: texts TextDetection[] OCR结果, language string 语言

    TextDetection: text string 文本, confidence int32 置信度, coordinates vector2[] 坐标
    :param image: 图片ID
    """
    count = 0

    def __init__(self, image: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class Voice(API):
    """
    语音
    https://docs.go-cqhttp.org/api/#%E8%AF%AD%E9%9F%B3
    """
    count = 0

    def __init__(self, api: str, data: dict):
        Voice.count += 1
        super().__init__(api, data)


class CanSendRecord(Voice):
    """
    检查是否可以发送语音
    https://docs.go-cqhttp.org/api/#%E6%A3%80%E6%9F%A5%E6%98%AF%E5%90%A6%E5%8F%AF%E4%BB%A5%E5%8F%91%E9%80%81%E8%AF%AD%E9%9F%B3

    响应数据: yes boolean 是或否
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class Handle(API):
    """
    处理
    https://docs.go-cqhttp.org/api/#%E5%A4%84%E7%90%86
    """
    count = 0

    def __init__(self, api: str, data: dict):
        Handle.count += 1
        super().__init__(api, data)


class SetFriendAddRequest(Handle):
    """
    处理加好友请求
    https://docs.go-cqhttp.org/api/#%E5%A4%84%E7%90%86%E5%8A%A0%E5%A5%BD%E5%8F%8B%E8%AF%B7%E6%B1%82

    响应数据: 该 API 无响应数据
    :param flag: 加好友请求的 flag（需从上报的数据中获得）
    :param approve: 是否同意请求
    :param remark: 添加后的好友备注（仅在同意时有效）
    """
    count = 0

    def __init__(self, flag: str, approve: bool = True, remark: str = ''):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupAddRequest(Handle):
    """
    处理加群请求／邀请
    https://docs.go-cqhttp.org/api/#%E5%A4%84%E7%90%86%E5%8A%A0%E7%BE%A4%E8%AF%B7%E6%B1%82-%E9%82%80%E8%AF%B7

    响应数据: 该 API 无响应数据
    :param flag: 加群请求的 flag（需从上报的数据中获得）
    :param sub_type: add 或 invite, 请求类型（需要和上报消息中的 sub_type 字段相符）
    :param approve: 是否同意请求／邀请
    :param reason: 拒绝理由（仅在拒绝时有效）
    """
    count = 0

    def __init__(self, flag: str, sub_type: str, approve: bool = True, reason: str = ''):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GroupInfo(API):
    """
    群信息
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E4%BF%A1%E6%81%AF
    """
    count = 0

    def __init__(self, api: str, data: dict):
        GroupInfo.count += 1
        super().__init__(api, data)


class GetGroupInfo(GroupInfo):
    """
    获取群信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E4%BF%A1%E6%81%AF

    响应数据: group_id int64 群号, group_name string 群名称, group_memo string 群备注, group_create_time uint32 群创建时间,
    group_level uint32 群等级, member_count int32 成员数, max_member_count int32 最大成员数（群容量）

    如果机器人尚未加入群, group_create_time, group_level, max_member_count 和 member_count 将会为0
    :param group_id: 群号
    :param no_cache: 是否不使用缓存（使用缓存可能更新不及时, 但响应更快）
    """
    count = 0

    def __init__(self, group_id: int, no_cache: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupList(GroupInfo):
    """
    获取群列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E5%88%97%E8%A1%A8

    响应数据: 响应内容为 json 数组, 每个元素和上面的 get_group_info 接口相同。
    :param no_cache: 是否不使用缓存（使用缓存可能更新不及时, 但响应更快）
    """
    count = 0

    def __init__(self, no_cache: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupMemberInfo(GroupInfo):
    """
    获取群成员信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%88%90%E5%91%98%E4%BF%A1%E6%81%AF

    响应数据: group_id int64 群号, user_id int64 QQ 号, nickname string 昵称, card string 群名片／备注,
    sex string 性别, male 或 female 或 unknown, age int32 年龄, area string 地区, join_time int32 加群时间戳,
    last_sent_time	int32	最后发言时间戳, level string 成员等级, role string 角色, owner 或 admin 或 member,
    unfriendly	boolean	是否不良记录成员, title string 专属头衔, title_expire_time int64 专属头衔过期时间戳,
    card_changeable boolean 是否允许修改群名片, shut_up_timestamp int64 禁言到期时间
    :param group_id: 群号
    :param user_id: QQ 号
    :param no_cache: 是否不使用缓存（使用缓存可能更新不及时, 但响应更快）
    """
    count = 0

    def __init__(self, group_id: int, user_id: int, no_cache: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupMemberList(GroupInfo):
    """
    获取群成员列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%88%90%E5%91%98%E5%88%97%E8%A1%A8

    响应数据: 响应内容为 json 数组, 每个元素的内容和上面的 get_group_member_info 接口相同,
    但对于同一个群组的同一个成员, 获取列表时和获取单独的成员信息时, 某些字段可能有所不同,
    例如 area、title 等字段在获取列表时无法获得, 具体应以单独的成员信息为准。
    :param group_id: 群号
    :param no_cache: 是否不使用缓存（使用缓存可能更新不及时, 但响应更快）
    """
    count = 0

    def __init__(self, group_id: int, no_cache: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupHonorInfo(GroupInfo):
    """
    获取群荣誉信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E8%8D%A3%E8%AA%89%E4%BF%A1%E6%81%AF

    响应数据: group_id int64 群号, current_talkative object 当前龙王, 仅 type 为 talkative 或 all 时有数据,
    talkative_list array 历史龙王, 仅type为talkative或all时有数据, performer_list array 群聊之火, 仅type为performer或all时有数据,
    legend_list	array 群聊炽焰, 仅type为legend或all时有数据, strong_newbie_list array 冒尖小春笋, 仅type为strong_newbie或all时有数据
    , emotion_list array 快乐之源, 仅 type 为 emotion 或 all 时有数据

    current_talkative 字段的内容如下: user_id int64 QQ 号, nickname str 昵称, avatar str 头像 URL, day_count int32 持续天数

    其它各 *_list 的每个元素是一个json对象,内容如下: user_id int QQ 号, nickname str 昵称, avatar str 头像 URL, description str 荣誉描述
    :param group_id: 群号
    :param type: 要获取的群荣誉类型,可传入talkative,performer,legend,strong_newbie,emotion以分别获取单个类型的群荣誉数据,或传入all获取所有数据
    """
    count = 0

    def __init__(self, group_id: int, type: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupSystemMsg(GroupInfo):
    """
    获取群系统消息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E7%B3%BB%E7%BB%9F%E6%B6%88%E6%81%AF

    响应数据: invited_requests InvitedRequest[] 邀请消息列表, join_requests JoinRequest[] 进群消息列表,
    如果列表不存在任何消息, 将返回 null

    InvitedRequest: request_id int64 请求ID, invitor_uin int64 邀请者, invitor_nick string 邀请者昵称, group_id int64 群号,
    group_name string 群名, checked bool 是否已被处理, actor int64 处理者, 未处理为0

    JoinRequest: request_id int64 请求ID, requester_uin int64 请求者ID, requester_nick str 请求者昵称,
    message str 验证消息, group_id int64 群号, group_name str 群名, checked bool 是否已被处理, actor int64 处理者, 未处理为0
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetEssenceMsgList(GroupInfo):
    """
    获取精华消息列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%B2%BE%E5%8D%8E%E6%B6%88%E6%81%AF%E5%88%97%E8%A1%A8

    响应数据: 响应内容为 JSON 数组，每个元素如下: sender_id int64 发送者QQ 号, sender_nick str 发送者昵称,
    sender_time int64 消息发送时间, operator_id int64 操作者QQ 号, operator_nick str 操作者昵称, operator_time int64 精华设置时间
    , message_id int32 消息ID
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupAtAllRemain(GroupInfo):
    """
    获取群 @全体成员 剩余次数
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4-%E5%85%A8%E4%BD%93%E6%88%90%E5%91%98-%E5%89%A9%E4%BD%99%E6%AC%A1%E6%95%B0

    响应数据: can_at_all bool 是否可以 @全体成员, remain_at_all_count_for_group int16 群内所有管理当天剩余 @全体成员 次数,
    remain_at_all_count_for_uin int16 Bot 当天剩余 @全体成员 次数
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GroupSetting(API):
    """
    群设置
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E8%AE%BE%E7%BD%AE
    """
    count = 0

    def __init__(self, api: str, data: dict):
        GroupInfo.count += 1
        __class__.count += 1
        super().__init__(api, data)


class SetGroupName(GroupSetting):
    """
    设置群名
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%BE%A4%E5%90%8D

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param group_name: 新群名
    """
    count = 0

    def __init__(self, group_id: int, group_name: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupPortrait(GroupSetting):
    r"""
    设置群头像
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%BE%A4%E5%A4%B4%E5%83%8F

    响应数据: 该 API 无响应数据

    1.file 参数支持以下几种格式:

    - 绝对路径, 例如 file:///C:\\Users\Richard\Pictures\1.png, 格式使用 file URI

    - 网络 URL, 例如 http://i1.piimg.com/567571/fdd6e7b6d93f1ef0.jpg

    - Base64 编码, 例如 base64://iVBORw0KGgoAAAANSUhEUgAAABQAAAAVCAIAAADJt1n/AAAAKElEQVQ4EWPk5+RmIBcwkasRpG9UM4mhNxpgowFGMARGEwnBIEJVAAAdBgBNAZf+QAAAAABJRU5ErkJggg==

    2.cache参数: 通过网络 URL 发送时有效, 1表示使用缓存, 0关闭关闭缓存, 默认 为 1

    3.目前这个API在登录一段时间后因cookie失效而失效, 请考虑后使用
    :param group_id: 群号
    :param file: 图片文件名
    :param cache: 表示是否使用已缓存的文件
    """
    count = 0

    def __init__(self, group_id: int, file: str, cache: int = 1):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupAdmin(GroupSetting):
    """
    设置群管理员
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%BE%A4%E7%AE%A1%E7%90%86%E5%91%98

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param user_id: 要设置管理员的 QQ 号
    :param enable: true 为设置, false 为取消
    """
    count = 0

    def __init__(self, group_id: int, user_id: int, enable: bool = True):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupCard(GroupSetting):
    """
    设置群名片 ( 群备注 )
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%BE%A4%E5%90%8D%E7%89%87-%E7%BE%A4%E5%A4%87%E6%B3%A8

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param user_id: 要设置的 QQ 号
    :param card: 群名片内容, 不填或空字符串表示删除群名片
    """
    count = 0

    def __init__(self, group_id: int, user_id: int, card: str = ''):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupSpecialTitle(GroupSetting):
    """
    设置群组专属头衔
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%BE%A4%E7%BB%84%E4%B8%93%E5%B1%9E%E5%A4%B4%E8%A1%94

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param user_id: 要设置的 QQ 号
    :param special_title: 专属头衔, 不填或空字符串表示删除专属头衔
    :param duration: 专属头衔有效期, 单位秒, -1 表示永久, 不过此项似乎没有效果, 可能是只有某些特殊的时间长度有效, 有待测试
    """
    count = 0

    def __init__(self, group_id: int, user_id: int, special_title: str = '', duration: int = -1):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GroupOperation(API):
    """
    群操作
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E6%93%8D%E4%BD%9C
    """
    count = 0

    def __init__(self, api: str, data: dict):
        GroupOperation.count += 1
        super().__init__(api, data)


class SetGroupBan(GroupOperation):
    """
    群单人禁言
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E5%8D%95%E4%BA%BA%E7%A6%81%E8%A8%80

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param user_id: 要禁言的 QQ 号
    :param duration: 禁言时长, 单位秒, 0 表示取消禁言
    """
    count = 0

    def __init__(self, group_id: int, user_id: int, duration: int = 1800):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupWholeBan(GroupOperation):
    """
    群全员禁言
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E5%85%A8%E5%91%98%E7%A6%81%E8%A8%80

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param enable: 是否禁言
    """
    count = 0

    def __init__(self, group_id: int, enable: bool = True):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupAnonymousBan(GroupOperation):
    """
    群匿名用户禁言
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E5%8C%BF%E5%90%8D%E7%94%A8%E6%88%B7%E7%A6%81%E8%A8%80

    anonymous 和 anonymous_flag 两者任选其一传入即可, 若都传入, 则使用 anonymous

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param anonymous: 可选, 要禁言的匿名用户对象（群消息上报的 anonymous 字段）
    :param anonymous_flag: 可选, 要禁言的匿名用户的 flag（需从群消息上报的数据中获得）
    :param duration: 禁言时长, 单位秒, 无法取消匿名用户禁言
    """
    count = 0

    def __init__(self, group_id: int, duration: int = 1800, anonymous: dict = None, anonymous_flag: str = ''):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetEssenceMsg(GroupOperation):
    """
    设置精华消息
    https://docs.go-cqhttp.org/api/#%E8%AE%BE%E7%BD%AE%E7%B2%BE%E5%8D%8E%E6%B6%88%E6%81%AF

    响应数据: 该 API 无响应数据
    :param message_id: 消息 ID
    """
    count = 0

    def __init__(self, message_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class DeleteEssenceMsg(GroupOperation):
    """
    移出精华消息
    https://docs.go-cqhttp.org/api/#%E7%A7%BB%E5%87%BA%E7%B2%BE%E5%8D%8E%E6%B6%88%E6%81%AF

    响应数据: 该 API 无响应数据
    :param message_id: 消息 ID
    """
    count = 0

    def __init__(self, message_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SendGroupSign(GroupOperation):
    """
    群打卡
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E6%89%93%E5%8D%A1

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class _SendGroupNotice(GroupOperation):
    """
    发送群公告
    https://docs.go-cqhttp.org/api/#%E5%8F%91%E9%80%81%E7%BE%A4%E5%85%AC%E5%91%8A

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param content: 公告内容
    :param image: 图片路径（可选）
    """
    count = 0

    def __init__(self, group_id: int, content: str, image: str = ''):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class _GetGroupNotice(GroupOperation):
    """
    获取群公告
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E5%85%AC%E5%91%8A

    响应数据: 响应内容为json数组，每个元素内容如下: sender_id int64 公告发表者, publish_time int 公告发表时间, message object 公告内容

    message 字段的内容如下: text string 公告内容, images array 公告图片

    images 字段每个元素内容如下: height string 图片高度, width string 图片宽度, id string 图片ID
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupKick(GroupOperation):
    """
    群组踢人
    https://docs.go-cqhttp.org/api/#%E7%BE%A4%E7%BB%84%E8%B8%A2%E4%BA%BA

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param user_id: 要踢的 QQ 号
    :param reject_add_request: 拒绝此人的加群请求
    """
    count = 0

    def __init__(self, group_id: int, user_id: int, reject_add_request: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class SetGroupLeave(GroupOperation):
    """
    退出群组
    https://docs.go-cqhttp.org/api/#%E9%80%80%E5%87%BA%E7%BE%A4%E7%BB%84

    响应数据: 该 API 无响应数据
    :param group_id: 群号
    :param is_dismiss: 是否解散, 如果登录号是群主, 则仅在此项为 true 时能够解散
    """
    count = 0

    def __init__(self, group_id: int, is_dismiss: bool = False):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class File(API):
    """
    文件
    https://docs.go-cqhttp.org/api/#%E6%96%87%E4%BB%B6
    """
    count = 0

    def __init__(self, api: str, data: dict):
        File.count += 1
        super().__init__(api, data)


class UploadGroupFile(File):
    """
    上传群文件
    https://docs.go-cqhttp.org/api/#%E4%B8%8A%E4%BC%A0%E7%BE%A4%E6%96%87%E4%BB%B6

    在不提供 folder 参数的情况下默认上传到根目录, 只能上传本地文件, 需要上传 http 文件的话请先调用 download_file API下载

    响应数据: 该API无响应数据
    :param group_id: 群号
    :param file: 本地文件路径
    :param name: 储存名称
    :param folder: 父目录ID
    """
    count = 0

    def __init__(self, group_id: int, file: str, name: str, folder: str = None):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class DeleteGroupFile(File):
    """
    删除群文件
    https://docs.go-cqhttp.org/api/#%E5%88%A0%E9%99%A4%E7%BE%A4%E6%96%87%E4%BB%B6

    响应数据: 该API无响应数据
    :param group_id: 群号
    :param file_id: 文件ID 参考 File 对象
    :param busid: 文件类型 参考 File 对象
    """
    count = 0

    def __init__(self, group_id: int, file_id: str, busid: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class CreateGroupFileFolder(File):
    """
    创建群文件文件夹
    https://docs.go-cqhttp.org/api/#%E5%88%9B%E5%BB%BA%E7%BE%A4%E6%96%87%E4%BB%B6%E6%96%87%E4%BB%B6%E5%A4%B9

    响应数据: 该API无响应数据
    :param group_id: 群号
    :param name: 文件夹名称
    :param parent_id: 仅能为 /
    """
    count = 0

    def __init__(self, group_id: int, name: str, parent_id: str = '/'):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class DeleteGroupFolder(File):
    """
    删除群文件文件夹
    https://docs.go-cqhttp.org/api/#%E5%88%A0%E9%99%A4%E7%BE%A4%E6%96%87%E4%BB%B6%E6%96%87%E4%BB%B6%E5%A4%B9

    响应数据: 该API无响应数据
    :param group_id: 群号
    :param folder_id: 文件夹ID 参考 File 对象
    """
    count = 0

    def __init__(self, group_id: int, folder_id: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupFileSystemInfo(File):
    """
    获取群文件系统信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E4%BF%A1%E6%81%AF

    响应数据: file_count int32 文件总数, limit_count int32 文件上限, used_space int64 已使用空间, total_space int64 空间上限
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupRootFiles(File):
    """
    获取群根目录文件列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%A0%B9%E7%9B%AE%E5%BD%95%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8

    响应数据: files File[] 文件列表, folders Folder[] 文件夹列表

    File: group_id int32 群号, file_id string 文件ID, file_name string 文件名, busid int32 文件类型, file_size int64 文件大小,
    upload_time int64 上传时间, dead_time int64 过期时间,永久文件恒为0, modify_time int64 最后修改时间,
    download_times int32 下载次数, uploader int64 上传者ID, uploader_name string 上传者名字

    Folder: group_id int32 群号, folder_id string 文件夹ID, folder_name string 文件名, create_time int64 创建时间,
    creator int64 创建者, creator_name string 创建者名字, total_file_count int32 子文件数量
    :param group_id: 群号
    """
    count = 0

    def __init__(self, group_id: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupFilesByFolder(File):
    """
    获取群子目录文件列表
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E5%AD%90%E7%9B%AE%E5%BD%95%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8

    响应数据: files File[] 文件列表, folders Folder[] 文件夹列表

    File: group_id int32 群号, file_id string 文件ID, file_name string 文件名, busid int32 文件类型, file_size int64 文件大小,
    upload_time int64 上传时间, dead_time int64 过期时间,永久文件恒为0, modify_time int64 最后修改时间,
    download_times int32 下载次数, uploader int64 上传者ID, uploader_name string 上传者名字

    Folder: group_id int32 群号, folder_id string 文件夹ID, folder_name string 文件名, create_time int64 创建时间,
    creator int64 创建者, creator_name string 创建者名字, total_file_count int32 子文件数量
    :param group_id: 群号
    :param folder_id: 文件夹ID 参考 Folder 对象
    """
    count = 0

    def __init__(self, group_id: int, folder_id: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetGroupFileUrl(File):
    """
    获取群文件资源链接
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%BE%A4%E6%96%87%E4%BB%B6%E8%B5%84%E6%BA%90%E9%93%BE%E6%8E%A5

    响应数据: url string 文件下载链接
    :param group_id: 群号
    :param file_id: 文件ID 参考 File 对象
    :param busid: 文件类型 参考 File 对象
    """
    count = 0

    def __init__(self, group_id: int, file_id: str, busid: int):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class UploadPrivateFile(File):
    """
    上传私聊文件
    https://docs.go-cqhttp.org/api/#%E4%B8%8A%E4%BC%A0%E7%A7%81%E8%81%8A%E6%96%87%E4%BB%B6

    只能上传本地文件, 需要上传 http 文件的话请先调用 download_file API下载

    响应数据: 该API无响应数据
    :param user_id: 对方 QQ 号
    :param file: 本地文件路径
    :param name: 文件名称
    """
    count = 0

    def __init__(self, user_id: int, file: str, name: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GoCqHttpRelated(API):
    """
    Go-CqHttp 相关
    https://docs.go-cqhttp.org/api/#go-cqhttp-%E7%9B%B8%E5%85%B3
    """
    count = 0

    def __init__(self, api: str, data: dict):
        GoCqHttpRelated.count += 1
        super().__init__(api, data)


class GetVersionInfo(GoCqHttpRelated):
    """
    获取版本信息
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%89%88%E6%9C%AC%E4%BF%A1%E6%81%AF

    响应数据: app_name string go-cqhttp 应用标识, 如 go-cqhttp 固定值, app_version string 应用版本, 如 v0.9.40-fix4,
    app_full_name string 应用完整名称, protocol_version string v11 OneBot 标准版本 固定值,
    coolq_edition string pro 原Coolq版本 固定值, coolq_directory string, go-cqhttp bool true 是否为go-cqhttp 固定值,
    plugin_version string 4.15.0 固定值, plugin_build_number int 99 固定值,
    plugin_build_configuration string release 固定值, runtime_version string, runtime_os string,
    version string 应用版本, 如 v0.9.40-fix4, protocol int 0/1/2/3/-1 当前登陆使用协议类型
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class GetStatus(GoCqHttpRelated):
    """
    获取状态
    https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%8A%B6%E6%80%81

    注意: 所有统计信息都将在重启后重置

    响应数据: app_initialized bool 原 CQHTTP 字段, 恒定为 true, app_enabled bool 原 CQHTTP 字段, 恒定为 true,
    plugins_good bool 原 CQHTTP 字段, 恒定为 true, app_good bool 原 CQHTTP 字段, 恒定为 true,
    online bool 表示BOT是否在线, good bool 同 online, stat Statistics 运行统计

    Statistics: PacketReceived uint64 收到的数据包总数, PacketSent uint64 发送的数据包总数, PacketLost uint32 数据包丢失总数,
    MessageReceived uint64 接受信息总数, MessageSent uint64 发送信息总数, DisconnectTimes uint32 TCP 链接断开次数,
    LostTimes uint32 账号掉线次数, LastMessageTime int64 最后一条消息时间
    """
    count = 0

    def __init__(self):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class ReloadEventFilter(GoCqHttpRelated):
    """
    重载事件过滤器
    https://docs.go-cqhttp.org/api/#%E9%87%8D%E8%BD%BD%E4%BA%8B%E4%BB%B6%E8%BF%87%E6%BB%A4%E5%99%A8

    响应数据: 该API无响应数据
    :param file: 事件过滤器文件
    """
    count = 0

    def __init__(self, file: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class DownloadFile(GoCqHttpRelated):
    r"""
    下载文件到缓存目录
    https://docs.go-cqhttp.org/api/#%E4%B8%8B%E8%BD%BD%E6%96%87%E4%BB%B6%E5%88%B0%E7%BC%93%E5%AD%98%E7%9B%AE%E5%BD%95

    通过这个API下载的文件能直接放入CQ码作为图片或语音发送，调用后会阻塞直到下载完成后才会返回数据，请注意下载大文件时的超时

    响应数据: file string 下载文件的绝对路径

    headers格式:

    字符串: User-Agent=YOUR_UA[\\r\\n]Referer=https://www.baidu.com
    提示: [\\r\\n] 为换行符, 使用http请求时请注意编码

    JSON数组:["User-Agent=YOUR_UA", "Referer=https://www.baidu.com"]
    :param url: 文件链接
    :param thread_count: 下载线程数
    :param headers: 自定义请求头
    """
    count = 0

    def __init__(self, url: str, thread_count: int, headers: str | dict):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())


class CheckUrlSafely(GoCqHttpRelated):
    """
    检查链接安全性
    https://docs.go-cqhttp.org/api/#%E6%A3%80%E6%9F%A5%E9%93%BE%E6%8E%A5%E5%AE%89%E5%85%A8%E6%80%A7

    响应数据: level int 安全等级, 1: 安全 2: 未知 3: 危险
    :param url: 需要检查的链接
    """
    count = 0

    def __init__(self, url: str):
        __class__.count += 1
        super().__init__(__class__.__name__, locals())
