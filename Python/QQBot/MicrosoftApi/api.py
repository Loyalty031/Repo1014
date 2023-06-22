"""Microsoft Graph API, currently only supports Microsoft To Do API, odata query options are not supported"""
import os
import json
import uuid
import base64
from models import *
from msconfig import config
from aiohttp import ClientSession
from abc import ABC, abstractmethod


class MicrosoftGraphAPI(ABC):
    """
    Microsoft Graph API基类，建议使用异步上下文管理器来执行操作

    不能直接创建此类的实例，因为有未实现的抽象方法
    """

    def __init__(self, token: str, session: ClientSession = None):
        """
        初始化一个Microsoft Graph API实例
        :param token: 执行操作所需的token
        :param session: 可选，一个aiohttp.ClientSession实例，如果不提供或提供错误的参数，将会自动创建一个
        """
        self.__token = token
        self._header = {'Authorization': 'Bearer ' + self.__token}
        self._session = session if isinstance(session, ClientSession) else None
        self._create_flag = self._session is None

    async def open(self):
        """
        打开一个会话，如果没有提供session参数，将会自动创建一个
        :return: None
        """
        if self._create_flag:
            self._session = ClientSession()

    async def close(self):
        """
        如果是自动创建的会话，将会关闭会话
        :return: None
        """
        if self._create_flag:
            await self._session.close()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @property
    def token(self) -> str:
        """
        返回当前实例的token
        :return: str
        """
        return self.__token

    @token.setter
    def token(self, token: str):
        """
        设置当前实例的token
        :param token: str
        """
        self.__token = token
        self._header['Authorization'] = 'Bearer ' + self.__token

    @classmethod
    @abstractmethod
    def scope(cls) -> list[str]:
        """
        API需要的权限范围
        :return: list[str]
        """


class TodoAPI(MicrosoftGraphAPI):
    """
    Microsoft To Do API基类

    创建此类的实例是没有意义的，因为此类没有直接实现任何API，请使用其子类。

    不应该直接调用此类的被保护的方法，请使用子类中封装好的方法。
    """

    @classmethod
    def scope(cls) -> list[str]:
        """
        To Do API的需要的权限范围
        :return: 权限范围
        """
        return ['Tasks.ReadWrite']

    async def _base_api(self, method, item_type, url: str, data: dict = None) -> list[BaseModel] | BaseModel | APIError:
        """
        To Do API的框架方法，用于发送请求并处理返回的数据，返回一个item_type实例或一个item_type实例列表，或者一个APIError实例
        :param method: 请求的方法，应该是self._session中的一个方法，如self._session.get
        :param item_type: 一个pydantic BaseModel的子类，用于将返回的数据转换为一个对象
        :param url: 请求的完整url
        :param data: 请求正文，以json格式传递
        :return: 如果是获取多个对象，返回一个item_type实例列表，如果是获取单个对象，返回一个item_type实例，如果出现错误，返回一个APIError实例
        """
        try:
            async with method(url, json=data, headers=self._header) as response:
                data = await response.json()
            if 'error' in data:
                return APIError(**data['error'])
            if isinstance(data['value'], list):
                return [item_type(**item) for item in data['value']]
            return item_type(**data['value'])
        except Exception as error:
            return APIError.from_exception(error)

    async def _delete_item(self, url: str, id: str) -> bool | APIError:
        """
        删除一个item（不能塞到框架里，故单独实现）
        :param url: 请求的完整url
        :param id: 要删除的item的id
        :return: 如果删除成功，返回True，否则返回一个APIError实例
        """
        try:
            async with self._session.delete(url + '/' + id, headers=self._header) as response:
                if response.status == 204:
                    return True
                return APIError(**(await response.json())['error'])
        except Exception as error:
            return APIError.from_exception(error)


class TodoTaskListAPI(TodoAPI):
    """
    Microsoft To Do API的任务列表相关操作
    """
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists'  # 基础终结点

    async def get_all_tasklists(self) -> list[TodoTaskList] | APIError:
        """
        获取所有的任务列表
        https://learn.microsoft.com/zh-cn/graph/api/todo-list-lists?view=graph-rest-1.0&tabs=http
        :return: 成功则返回所有TodoTaskList实例列表，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, TodoTaskList, TodoTaskListAPI.__base_url)

    async def create_tasklist(self, display_name: str) -> TodoTaskList | APIError:
        """
        创建一个任务列表
        https://learn.microsoft.com/zh-cn/graph/api/todo-post-lists?view=graph-rest-1.0&tabs=http
        :param display_name: 任务列表的显示名称
        :return: 成功则返回创建的TodoTaskList实例，失败则返回一个APIError实例
        """
        return await self._base_api(
            method=self._session.post,
            item_type=TodoTaskList,
            url=TodoTaskListAPI.__base_url,
            data={"displayName": display_name}
        )

    async def get_one_tasklist(self, id: str) -> TodoTaskList | APIError:
        """
        获取一个任务列表
        https://learn.microsoft.com/zh-cn/graph/api/todotasklist-get?view=graph-rest-1.0&tabs=http
        :param id: 任务列表的id
        :return: 成功则返回该TodoTaskList实例，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, TodoTaskList, TodoTaskListAPI.__base_url + '/' + id)

    async def update_tasklist(self, id: str, display_name: str) -> TodoTaskList | APIError:
        """
        更新一个任务列表
        https://learn.microsoft.com/zh-cn/graph/api/todotasklist-update?view=graph-rest-1.0&tabs=http
        :param id: 任务列表的id
        :param display_name: 任务列表的新显示名称
        :return: 成功则返回更新后的TodoTaskList实例，失败则返回一个APIError实例
        """
        return await self._base_api(
            method=self._session.patch,
            item_type=TodoTaskList,
            url=TodoTaskListAPI.__base_url + '/' + id,
            data={"displayName": display_name}
        )

    async def delete_tasklist(self, id: str) -> bool | APIError:
        """
        删除一个任务列表
        https://learn.microsoft.com/zh-cn/graph/api/todotasklist-delete?view=graph-rest-1.0&tabs=http
        :param id: 任务列表的id
        :return: 成功则返回True，失败则返回一个APIError实例
        """
        return await self._delete_item(TodoTaskListAPI.__base_url, id)


class TodoTaskAPI(TodoAPI):
    """
    Microsoft To Do API的任务相关操作
    """
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks'  # tasklist_id

    def __init__(self, token: str, tasklist_id: str, session: ClientSession = None):
        """
        初始化一个TodoTaskAPI实例
        :param token: 执行操作所需的token
        :param tasklist_id: 任务列表的id
        :param session: 可选，如果不传入则会自动创建一个ClientSession
        """
        super().__init__(token, session)
        self.__base_url = TodoTaskAPI.__base_url.format(tasklist_id)

    async def get_all_tasks(self) -> list[TodoTask] | APIError:
        """
        获取所有的任务
        https://learn.microsoft.com/zh-cn/graph/api/todotasklist-list-tasks?view=graph-rest-1.0&tabs=http
        :return: 成功则返回所有TodoTask实例列表，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, TodoTask, self.__base_url)

    async def create_task(
            self,
            id: str = None,
            body: ItemBody = None,
            categories: list[str] = None,
            completedDateTime: DateTimeTimeZone = None,
            dueDateTime: DateTimeTimeZone = None,
            importance: TodoTaskImportance = None,
            isReminderOn: bool = None,
            recurrence: PatternedRecurrence = None,
            reminderDateTime: DateTimeTimeZone = None,
            startDateTime: DateTimeTimeZone = None,
            status: TodoTaskStatus = None,
            title: str = None,
            createdDateTime: datetime | str = None,
            lastModifiedDateTime: datetime | str = None,
            bodyLastModifiedDateTime: datetime | str = None,
            linkedResources: list[LinkedResource] = None,
    ) -> TodoTask | APIError:
        """
        创建一个任务，所有参数均是可选的，只需要传入已有的参数即可
        https://learn.microsoft.com/zh-cn/graph/api/todotasklist-post-tasks?view=graph-rest-1.0&tabs=http
        :param id: 任务的id(极少情况下需要手动指定)
        :param body: 一个ItemBody实例，表示任务的正文
        :param categories: 一个字符串列表，表示任务的分类
        :param completedDateTime: 一个DateTimeTimeZone实例，表示任务的完成时间
        :param dueDateTime: 一个DateTimeTimeZone实例，表示任务的截止时间
        :param importance: 一个TodoTaskImportance实例，表示任务的重要性
        :param isReminderOn: 一个布尔值，表示是否提醒
        :param recurrence: 一个PatternedRecurrence实例，表示任务的重复规则
        :param reminderDateTime: 一个DateTimeTimeZone实例，表示任务的提醒时间
        :param startDateTime: 一个DateTimeTimeZone实例，表示任务的开始时间
        :param status: 一个TodoTaskStatus实例，表示任务的状态
        :param title: 任务的标题
        :param createdDateTime: 任务的创建时间
        :param lastModifiedDateTime: 任务的最后修改时间
        :param bodyLastModifiedDateTime: 任务正文的最后修改时间
        :param linkedResources: 一个LinkedResource实例列表，表示任务的链接资源
        :return: 成功则返回创建的TodoTask实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, BaseModel):
                    data[key] = json.loads(value.json(exclude_none=True))
                else:
                    data[key] = value
        if 'linkedResources' in data:
            data['linkedResources'] = [item.dict(exclude_none=True) for item in data['linkedResources']]
        return await self._base_api(
            method=self._session.post,
            item_type=TodoTask,
            url=self.__base_url,
            data=data
        )

    async def get_one_task(self, id: str) -> TodoTask | APIError:
        """
        获取一个任务
        https://learn.microsoft.com/zh-cn/graph/api/todotask-get?view=graph-rest-1.0&tabs=http
        :param id: 任务的id
        :return: 成功则返回TodoTask实例，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, TodoTask, self.__base_url + '/' + id)

    async def update_task(
            self,
            id: str,
            body: ItemBody = None,
            categories: list[str] = None,
            completedDateTime: DateTimeTimeZone = None,
            dueDateTime: DateTimeTimeZone = None,
            importance: TodoTaskImportance = None,
            isReminderOn: bool = None,
            recurrence: PatternedRecurrence = None,
            reminderDateTime: DateTimeTimeZone = None,
            startDateTime: DateTimeTimeZone = None,
            status: TodoTaskStatus = None,
            title: str = None,
            createdDateTime: datetime | str = None,
            lastModifiedDateTime: datetime | str = None,
            bodyLastModifiedDateTime: datetime | str = None,
            linkedResources: list[LinkedResource] = None,
    ) -> TodoTask | APIError:
        """
        更新一个任务，所有参数均是可选的，只需要传入需要修改的参数即可
        https://learn.microsoft.com/zh-cn/graph/api/todotask-update?view=graph-rest-1.0&tabs=http
        :param id: 任务的id
        :param body: 任务的正文
        :param categories: 任务的分类
        :param completedDateTime: 任务的完成时间
        :param dueDateTime: 任务的截止时间
        :param importance: 任务的重要性
        :param isReminderOn: 是否提醒
        :param recurrence: 任务的重复规则
        :param reminderDateTime: 任务的提醒时间
        :param startDateTime: 任务的开始时间
        :param status: 任务的状态
        :param title: 任务的标题
        :param createdDateTime: 任务的创建时间
        :param lastModifiedDateTime: 任务的最后修改时间
        :param bodyLastModifiedDateTime: 任务正文的最后修改时间
        :param linkedResources: 任务的链接资源
        :return: 成功则返回更新后的TodoTask实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        kwargs.pop('id')
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, BaseModel):
                    data[key] = json.loads(value.json(exclude_none=True))
                else:
                    data[key] = value
        if 'linkedResources' in data:
            data['linkedResources'] = [item.dict(exclude_none=True) for item in data['linkedResources']]
        return await self._base_api(
            method=self._session.patch,
            item_type=TodoTask,
            url=self.__base_url + '/' + id,
            data=data
        )

    async def delete_task(self, id: str) -> bool | APIError:
        """
        删除一个任务
        https://learn.microsoft.com/zh-cn/graph/api/todotask-delete?view=graph-rest-1.0&tabs=http
        :param id: 任务的id
        :return: 成功则返回True，失败则返回一个APIError实例
        """
        return await self._delete_item(self.__base_url, id)


class TaskFileAttachmentAPI(TodoAPI):
    """
    Microsoft To Do API的附件相关操作
    """
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}/attachments'  # tasklist_id, task_id

    def __init__(self, token: str, tasklist_id: str, task_id: str, session: ClientSession = None):
        """
        初始化一个TaskFileAttachmentAPI实例
        :param token: 执行操作所需的token
        :param tasklist_id: 任务列表的id
        :param task_id: 任务的id
        :param session: 可选，如果不传入则会自动创建一个ClientSession
        """
        super().__init__(token, session)
        self.__base_url = TaskFileAttachmentAPI.__base_url.format(tasklist_id, task_id)

    @staticmethod
    def save_attachment(attachment: TaskFileAttachment, path: str = r'.\temp\attachment') -> str:
        """
        保存附件到本地
        :param attachment: 要保存的附件
        :param path: 可选，保存的路径
        :return: 保存的文件路径
        """
        if not os.path.exists(path):
            os.makedirs(path)
        if attachment.name is None or attachment.name == '':
            filename = uuid.uuid4().hex
        else:
            filename = attachment.name
        filepath = path + '\\' + filename
        with open(filepath, 'wb') as file:
            file.write(base64.b64decode(attachment.contentBytes))
        return filepath

    async def get_all_attachments(self) -> list[TaskFileAttachment] | APIError:
        """
        获取所有附件
        https://learn.microsoft.com/zh-cn/graph/api/todotask-list-attachments?view=graph-rest-1.0&tabs=http
        :return: 成功则返回一个TaskFileAttachment实例列表，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, TaskFileAttachment, self.__base_url)

    async def get_one_attachment(self, id: str) -> TaskFileAttachment | APIError:
        """
        获取一个附件
        https://learn.microsoft.com/zh-cn/graph/api/taskfileattachment-get?view=graph-rest-1.0&tabs=http
        :param id: 附件的id
        :return: 成功则返回一个TaskFileAttachment实例，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, TaskFileAttachment, self.__base_url + '/' + id)

    async def delete_attachment(self, id: str) -> bool | APIError:
        """
        删除一个附件
        https://learn.microsoft.com/zh-cn/graph/api/taskfileattachment-delete?view=graph-rest-1.0&tabs=http
        :param id: 附件的id
        :return: 成功则返回True，失败则返回一个APIError实例
        """
        return await self._delete_item(self.__base_url, id)

    async def upload_big_attachment(self, filepath: str, info: AttachmentInfo) -> str | APIError:
        """
        上传一个大附件(0-25MB)
        https://learn.microsoft.com/zh-cn/graph/api/taskfileattachment-createuploadsession?view=graph-rest-1.0&tabs=http
        :param filepath: 附件的路径，只支持本地文件
        :param info: 附件的信息
        :return: 成功则返回附件的Location，失败则返回一个APIError实例
        """
        try:  # 获取上传地址，读取本地文件
            async with self._session.post(url=self.__base_url + '/createUploadSession',
                                          json={'attachmentInfo': info.dict(exclude_none=True)},
                                          headers=self._header) as response:
                data = await response.json()
            if 'error' in data:
                return APIError(**data['error'])
            upload_url = data['uploadUrl']
            put_header = self._header.copy()
            with open(filepath, 'rb') as file:
                contents = file.read()
        except Exception as error:
            return APIError.from_exception(error)
        try:  # 上传文件
            while True:
                expect_range = data['nextExpectedRanges'][0].split('-')
                if len(expect_range) == 1 or expect_range[1] == '':
                    expect_range = [int(expect_range[0])]
                    length = int(min(info.size - int(expect_range[0]), config.upload_limit_mb * (1024 ** 2)))
                else:
                    expect_range = [int(expect_range[0]), int(expect_range[1])]
                    length = int(expect_range[1] - expect_range[0] + 1)
                put_header.update({
                    'Content-Length': str(length),
                    'Content-Range': 'bytes {}-{}/{}'.format(
                        expect_range[0],
                        expect_range[0] + length - 1,
                        info.size
                    ),
                    'Content-Type': 'application/octet-stream'
                })
                current_content = contents[int(expect_range[0]):int(expect_range[0] + length)]
                async with self._session.put(upload_url + '/content', data=current_content,
                                             headers=put_header) as response:
                    status = response.status
                    if status == 200:
                        data = await response.json()
                    elif status == 201:
                        return response.headers['Location']
                    else:
                        async with self._session.delete(upload_url):
                            return APIError(**(await response.json())['error'])
        except Exception as error:
            try:
                async with self._session.delete(upload_url):
                    return APIError.from_exception(error)
            except Exception as error:
                return APIError.from_exception(error)

    async def upload_small_attachment(
            self,
            contentBytes: bytes,
            contentType: str,
            name: str,
            size: int
    ) -> TaskFileAttachment | APIError:
        """
        上传一个小附件(0-3MB)
        https://learn.microsoft.com/zh-cn/graph/api/todotask-post-attachments?view=graph-rest-1.0&tabs=http
        :param contentBytes: 附件的内容
        :param contentType: 附件的类型
        :param name: 附件的名称
        :param size: 附件的大小
        :return: 成功则返回一个TaskFileAttachment实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        kwargs.update({
            "@odata.type": "#microsoft.graph.taskFileAttachment",
            "contentBytes": base64.b64encode(contentBytes).decode()
        })
        return await self._base_api(
            method=self._session.post,
            item_type=TaskFileAttachment,
            url=self.__base_url,
            data=kwargs
        )


class CheckListItemAPI(TodoAPI):
    """
    Microsoft To Do API的清单项相关操作
    """
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}/checklistItems'  # tasklist_id, task_id

    def __init__(self, token: str, tasklist_id: str, task_id: str, session: ClientSession = None):
        """
        初始化一个CheckListItemAPI实例
        :param token: 执行操作所需的token
        :param tasklist_id: 任务列表的id
        :param task_id: 任务的id
        :param session: 可选，如果不传入则会自动创建一个ClientSession
        """
        super().__init__(token, session)
        self.__base_url = CheckListItemAPI.__base_url.format(tasklist_id, task_id)

    async def get_all_checklistitems(self) -> list[CheckListItem] | APIError:
        """
        获取所有清单项
        https://learn.microsoft.com/zh-cn/graph/api/todotask-list-checklistitems?view=graph-rest-1.0&tabs=http
        :return: 成功则返回一个CheckListItem实例列表，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, CheckListItem, self.__base_url)

    async def create_checklistitem(self, displayName: str, isChecked: bool = False) -> CheckListItem | APIError:
        """
        创建一个清单项
        https://learn.microsoft.com/zh-cn/graph/api/todotask-post-checklistitems?view=graph-rest-1.0&tabs=http
        :param displayName: 清单项的名称
        :param isChecked: 清单项是否已完成
        :return: 成功则返回一个CheckListItem实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        return await self._base_api(self._session.post, CheckListItem, self.__base_url, kwargs)

    async def get_one_checklistitem(self, id: str) -> CheckListItem | APIError:
        """
        获取一个清单项
        https://learn.microsoft.com/zh-cn/graph/api/checklistitem-get?view=graph-rest-1.0&tabs=http
        :param id: 清单项的id
        :return: 成功则返回一个CheckListItem实例，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, CheckListItem, self.__base_url + '/' + id)

    async def update_checklistitem(self, id: str, displayName: str = None,
                                   isChecked: bool = None) -> CheckListItem | APIError:
        """
        更新一个清单项
        https://learn.microsoft.com/zh-cn/graph/api/checklistitem-update?view=graph-rest-1.0&tabs=http
        :param id: 要更新的清单项的id
        :param displayName: 清单项的名称
        :param isChecked: 清单项是否已完成
        :return: 成功则返回一个CheckListItem实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        kwargs.pop('id')
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return await self._base_api(self._session.patch, CheckListItem, self.__base_url + '/' + id, kwargs)

    async def delete_checklistitem(self, id: str) -> bool | APIError:
        """
        删除一个清单项
        https://learn.microsoft.com/zh-cn/graph/api/checklistitem-delete?view=graph-rest-1.0&tabs=http
        :param id: 要删除的清单项的id
        :return: 成功则返回True，失败则返回一个APIError实例
        """
        return await self._delete_item(self.__base_url, id)


class LinkedResourceAPI(TodoAPI):
    """
    Microsoft To Do API的链接资源相关操作
    """
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}/linkedResources'  # tasklist_id, task_id

    def __init__(self, token: str, tasklist_id: str, task_id: str, session: ClientSession = None):
        """
        初始化一个LinkedResourceAPI实例
        :param token: 执行操作所需的token
        :param tasklist_id: 任务列表的id
        :param task_id: 任务的id
        :param session: 可选，如果不传入则会自动创建一个ClientSession
        """
        super().__init__(token, session)
        self.__base_url = LinkedResourceAPI.__base_url.format(tasklist_id, task_id)

    async def get_all_linkedresources(self) -> list[LinkedResource] | APIError:
        """
        获取所有链接资源
        https://learn.microsoft.com/zh-cn/graph/api/todotask-list-linkedresources?view=graph-rest-1.0&tabs=http
        :return: 成功则返回一个LinkedResource实例列表，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, LinkedResource, self.__base_url)

    async def create_linkedresource(
            self,
            id: str = None,
            displayName: str = None,
            applicationName: str = None,
            externalId: str = None,
            webUrl: str = None
    ) -> LinkedResource | APIError:
        """
        创建一个链接资源
        https://learn.microsoft.com/zh-cn/graph/api/todotask-post-linkedresources?view=graph-rest-1.0&tabs=http
        :param id: 链接资源的id，极少情况下需要手动指定
        :param displayName: 链接资源的名称
        :param applicationName: 链接资源的应用名称
        :param externalId: 链接资源的外部id
        :param webUrl: 链接资源的网页链接
        :return: 成功则返回一个LinkedResource实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return await self._base_api(self._session.post, LinkedResource, self.__base_url, kwargs)

    async def get_one_linkedresource(self, id: str) -> LinkedResource | APIError:
        """
        获取一个链接资源
        https://learn.microsoft.com/zh-cn/graph/api/linkedresource-get?view=graph-rest-1.0&tabs=http
        :param id: 链接资源的id
        :return: 成功则返回一个LinkedResource实例，失败则返回一个APIError实例
        """
        return await self._base_api(self._session.get, LinkedResource, self.__base_url + '/' + id)

    async def update_linkedresource(
            self,
            id: str,
            displayName: str = None,
            applicationName: str = None,
            externalId: str = None,
            webUrl: str = None
    ) -> LinkedResource | APIError:
        """
        更新一个链接资源
        https://learn.microsoft.com/zh-cn/graph/api/linkedresource-update?view=graph-rest-1.0&tabs=http
        :param id: 链接资源的id
        :param displayName: 链接资源的名称
        :param applicationName: 链接资源的应用名称
        :param externalId: 链接资源的外部id
        :param webUrl: 链接资源的网页链接
        :return: 成功则返回一个LinkedResource实例，失败则返回一个APIError实例
        """
        kwargs = locals()
        kwargs.pop('self')
        kwargs.pop('id')
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return await self._base_api(self._session.patch, LinkedResource, self.__base_url + '/' + id, kwargs)

    async def delete_linkedresource(self, id: str) -> bool | APIError:
        """
        删除一个链接资源
        https://learn.microsoft.com/zh-cn/graph/api/linkedresource-delete?view=graph-rest-1.0&tabs=http
        :param id: 链接资源的id
        :return: 成功则返回True，失败则返回一个APIError实例
        """
        return await self._delete_item(self.__base_url, id)
