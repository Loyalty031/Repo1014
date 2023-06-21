import msal
from msconfig import config
from models import Token, DeviceFlow


class Graph(object):
    def __init__(self, scopes: list[str]):
        self.__scopes = scopes  # 看过msal源代码了，这里不需要去重，msal内部会去重
        self.__app = msal.PublicClientApplication(
            client_id=config.client_id,
            authority=config.authority
        )
        self.__device_flow = DeviceFlow(**self.__app.initiate_device_flow(scopes=self.__scopes))
        self.__token: Token | None = None

    @property
    def token(self) -> str:
        return self.__token.access_token

    @property
    def login_message(self) -> str:
        return "浏览器打开:{}\n输入设备代码：{}\n{}分钟内有效".format(
            self.__device_flow.verification_uri,
            self.__device_flow.user_code,
            int(self.__device_flow.expires_in / 60)
        )

    def login(self) -> str:
        self.__token = Token(**self.__app.acquire_token_by_device_flow(self.__device_flow.dict()))
        return self.token

    def logout(self) -> None:
        self.__app.remove_account(self.__app.get_accounts()[0])
        self.__token = None

    def refresh(self) -> str:
        self.__token = Token(**self.__app.acquire_token_silent(
            scopes=self.__scopes,
            account=self.__app.get_accounts()[0],
            force_refresh=True
        ))
        return self.token
