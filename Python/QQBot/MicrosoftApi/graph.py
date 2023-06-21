"""Graph App"""
from msconfig import config
from models import Token, DeviceFlow
from msal import PublicClientApplication


class GraphApp(object):
    """
    Graph App

    通过设备流获取token，在API调用时需要用到token
    """

    def __init__(self, scopes: list[str] | str, client_id: str = None, authority: str = None):
        """
        初始化一个GraphApp实例
        :param scopes: 权限列表，可以是字符串列表或者空格分隔的字符串
        :param client_id: 可选，应用程序ID，如果不提供则使用配置文件中的client_id
        :param authority: 可选，标识令牌授权机构的URL，如果不提供则使用配置文件中的authority
        """
        self.__scopes = scopes if isinstance(scopes, list) else scopes.split()  # 这里不需要去重，msal内部会去重
        self.__app = PublicClientApplication(
            client_id=client_id or config.client_id,
            authority=authority or config.authority
        )
        self.__device_flow = DeviceFlow(**self.__app.initiate_device_flow(scopes=self.__scopes))
        self.__token: Token | None = None

    @property
    def token(self) -> str:
        """
        获取token
        :return: token
        """
        return self.__token.access_token

    @property
    def scopes(self) -> list[str]:
        """
        获取权限列表
        :return: 权限列表
        """
        if self.__token is not None:
            return self.__token.scope.split()
        return self.__scopes

    @property
    def login_message(self) -> str:
        """
        获取登录提示信息
        :return: 登录提示信息
        """
        return "浏览器打开:{}\n输入设备代码：{}\n{}分钟内有效".format(
            self.__device_flow.verification_uri,
            self.__device_flow.user_code,
            int(self.__device_flow.expires_in / 60)
        )

    def login(self) -> str:
        """
        使用设备流登录。

        先向用户发送self.login_message中的登录信息，用户根据提示完成登录。

        用户未完成登录时会阻塞当前线程。
        :return: token
        """
        self.__token = Token(**self.__app.acquire_token_by_device_flow(self.__device_flow.dict()))
        return self.token

    def logout(self) -> None:
        """
        登出
        :return: None
        """
        self.__app.remove_account(self.__app.get_accounts()[0])
        self.__token = None

    def refresh(self) -> str:
        """
        获取的token有效期过后，使用此函数刷新token
        :return: token
        """
        self.__token = Token(**self.__app.acquire_token_silent(
            scopes=self.__scopes,
            account=self.__app.get_accounts()[0],
            force_refresh=True
        ))
        return self.token
