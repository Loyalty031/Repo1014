import os
import abc
import sys
import json
import uuid
import base64
import aiohttp
from models import *
from msconfig import config


class MicrosoftAPI(abc.ABC):
    def __init__(self, token: str, session: aiohttp.ClientSession = None):
        self._header = {'Authorization': 'Bearer ' + token}
        self._session = session
        self._create_flag = self._session is None

    async def open(self):
        if self._create_flag:
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._create_flag:
            await self._session.close()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @classmethod
    @abc.abstractmethod
    def scope(cls) -> list[str]:
        """
        API需要的权限范围
        :return: list[str]
        """


class TodoAPI(MicrosoftAPI):
    @classmethod
    def scope(cls) -> list[str]:
        return ['Tasks.ReadWrite']

    async def _base_api(self, method, item_type, url: str, data: dict = None) -> list[BaseModel] | BaseModel | APIError:
        try:
            async with method(url, json=data, headers=self._header) as response:
                data = await response.json()
            if 'error' in data:
                return APIError(**data['error'])
            if isinstance(data['value'], list):
                return [item_type(**item) for item in data['value']]
            return item_type(**data['value'])
        except Exception as error:
            return APIError.from_exception(error, sys.exc_info())

    async def _delete_item(self, url: str, id: str) -> bool | APIError:
        try:
            async with self._session.delete(url + '/' + id, headers=self._header) as response:
                if response.status == 204:
                    return True
                return APIError(**(await response.json())['error'])
        except Exception as error:
            return APIError.from_exception(error, sys.exc_info())


class TodoTaskListAPI(TodoAPI):
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists'

    async def get_all_tasklists(self) -> list[TodoTaskList] | APIError:
        return await self._base_api(self._session.get, TodoTaskList, TodoTaskListAPI.__base_url)

    async def create_tasklist(self, display_name: str) -> TodoTaskList | APIError:
        return await self._base_api(
            method=self._session.post,
            item_type=TodoTaskList,
            url=TodoTaskListAPI.__base_url,
            data={"displayName": display_name}
        )

    async def get_one_tasklist(self, id: str) -> TodoTaskList | APIError:
        return await self._base_api(self._session.get, TodoTaskList, TodoTaskListAPI.__base_url + '/' + id)

    async def update_tasklist(self, id: str, display_name: str) -> TodoTaskList | APIError:
        return await self._base_api(
            method=self._session.patch,
            item_type=TodoTaskList,
            url=TodoTaskListAPI.__base_url + '/' + id,
            data={"displayName": display_name}
        )

    async def delete_tasklist(self, id: str) -> bool | APIError:
        return await self._delete_item(TodoTaskListAPI.__base_url, id)


class TodoTaskAPI(TodoAPI):
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks'

    def __init__(self, token: str, tasklist_id: str, session: aiohttp.ClientSession = None):
        super().__init__(token, session)
        self.__base_url = TodoTaskAPI.__base_url.format(tasklist_id)

    async def get_all_tasks(self) -> list[TodoTask] | APIError:
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
        return await self._delete_item(self.__base_url, id)


class TaskFileAttachmentAPI(TodoAPI):
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}/attachments'

    def __init__(self, token: str, tasklist_id: str, task_id: str, session: aiohttp.ClientSession = None):
        super().__init__(token, session)
        self.__base_url = TaskFileAttachmentAPI.__base_url.format(tasklist_id, task_id)

    @staticmethod
    def save_attachment(attachment: TaskFileAttachment, path: str = r'.\temp\attachment') -> str:
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
        return await self._base_api(self._session.get, TaskFileAttachment, self.__base_url)

    async def get_one_attachment(self, id: str) -> TaskFileAttachment | APIError:
        return await self._base_api(self._session.get, TaskFileAttachment, self.__base_url + '/' + id)

    async def delete_attachment(self, id: str) -> bool | APIError:
        return await self._delete_item(self.__base_url, id)

    async def upload_big_attachment(self, filepath: str, info: AttachmentInfo) -> str | APIError:
        async with self._session.post(url=self.__base_url + '/createUploadSession',
                                      json={'attachmentInfo': info.dict(exclude_none=True)},
                                      headers=self._header) as response:
            data = await response.json()
        if 'error' in data:
            return APIError(**data['error'])
        upload_url = data['uploadUrl']
        try:
            put_header = self._header.copy()
            with open(filepath, 'rb') as file:
                contents = file.read()
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
            async with self._session.delete(upload_url):
                return APIError(code=error.__class__.__name__, message=str(error))

    async def upload_small_attachment(
            self,
            contentBytes: bytes,
            contentType: str,
            name: str,
            size: int
    ) -> TaskFileAttachment | APIError:
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
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}/checklistItems'

    def __init__(self, token: str, tasklist_id: str, task_id: str, session: aiohttp.ClientSession = None):
        super().__init__(token, session)
        self.__base_url = CheckListItemAPI.__base_url.format(tasklist_id, task_id)

    async def get_all_checklistitems(self) -> list[CheckListItem] | APIError:
        return await self._base_api(self._session.get, CheckListItem, self.__base_url)

    async def create_checklistitem(self, displayName: str, isChecked: bool = False) -> CheckListItem | APIError:
        kwargs = locals()
        kwargs.pop('self')
        return await self._base_api(self._session.post, CheckListItem, self.__base_url, kwargs)

    async def get_one_checklistitem(self, id: str) -> CheckListItem | APIError:
        return await self._base_api(self._session.get, CheckListItem, self.__base_url + '/' + id)

    async def update_checklistitem(self, id: str, displayName: str = None,
                                   isChecked: bool = None) -> CheckListItem | APIError:
        kwargs = locals()
        kwargs.pop('self')
        kwargs.pop('id')
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return await self._base_api(self._session.patch, CheckListItem, self.__base_url + '/' + id, kwargs)

    async def delete_checklistitem(self, id: str) -> bool | APIError:
        return await self._delete_item(self.__base_url, id)


class LinkedResourceAPI(TodoAPI):
    __base_url = 'https://graph.microsoft.com/v1.0/me/todo/lists/{}/tasks/{}/linkedResources'

    def __init__(self, token: str, tasklist_id: str, task_id: str, session: aiohttp.ClientSession = None):
        super().__init__(token, session)
        self.__base_url = LinkedResourceAPI.__base_url.format(tasklist_id, task_id)

    async def get_all_linkedresources(self) -> list[LinkedResource] | APIError:
        return await self._base_api(self._session.get, LinkedResource, self.__base_url)

    async def create_linkedresource(
            self,
            id: str = None,
            displayName: str = None,
            applicationName: str = None,
            externalId: str = None,
            webUrl: str = None
    ) -> LinkedResource | APIError:
        kwargs = locals()
        kwargs.pop('self')
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return await self._base_api(self._session.post, LinkedResource, self.__base_url, kwargs)

    async def get_one_linkedresource(self, id: str) -> LinkedResource | APIError:
        return await self._base_api(self._session.get, LinkedResource, self.__base_url + '/' + id)

    async def update_linkedresource(
            self,
            id: str,
            displayName: str = None,
            applicationName: str = None,
            externalId: str = None,
            webUrl: str = None
    ) -> LinkedResource | APIError:
        kwargs = locals()
        kwargs.pop('self')
        kwargs.pop('id')
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        return await self._base_api(self._session.patch, LinkedResource, self.__base_url + '/' + id, kwargs)

    async def delete_linkedresource(self, id: str) -> bool | APIError:
        return await self._delete_item(self.__base_url, id)
