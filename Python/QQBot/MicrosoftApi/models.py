from enum import Enum
from datetime import datetime, date
from pydantic import BaseModel, Field, Required, HttpUrl


class Config(BaseModel):
    authority: str = Field(
        Required,
        title='授权地址',
        description='授权地址，例如：`https://login.microsoftonline.com/common`',
        example='https://login.microsoftonline.com/common'
    )
    client_id: str = Field(
        Required,
        title='客户端标识符',
        description='客户端标识符，例如：`00000000-0000-0000-0000-000000000000`',
        example='00000000-0000-0000-0000-000000000000'
    )
    upload_limit_mb: float = Field(
        Required,
        title='上传限制',
        description='单次上传限制，单位：MB',
        le=4
    )


class APIError(BaseModel):
    code: str = Field(
        Required,
        title='错误代码',
        description='错误代码'
    )
    message: str = Field(
        Required,
        title='错误消息',
        description='错误消息'
    )
    innerError: dict[str, str] = Field(
        None,
        title='内部错误',
        description='内部错误'
    )

    @classmethod
    def from_exception(cls, exception: Exception, info: list[str] = None) -> 'APIError':
        return APIError(
            code=exception.__class__.__name__,
            message=str(exception),
            innerError={'stack': ''.join(info)} if info else None
        )


class DeviceFlow(BaseModel):
    user_code: str = Field(
        Required,
        title='用户代码',
        description='用户代码'
    )
    device_code: str = Field(
        Required,
        title='设备代码',
        description='设备代码'
    )
    verification_uri: HttpUrl = Field(
        Required,
        title='验证地址',
        description='验证地址'
    )
    expires_in: int = Field(
        Required,
        title='过期时间',
        description='过期时间，单位：秒'
    )
    interval: int = Field(
        Required,
        title='间隔时间',
        description='间隔时间，单位：秒'
    )
    message: str = Field(
        Required,
        title='消息',
        description='消息'
    )
    expires_at: float = Field(
        Required,
        title='过期时间戳',
        description='过期时间戳'
    )
    _correlation_id: str = Field(
        Required,
        title='关联标识符',
        description='关联标识符'
    )


class Token(BaseModel):
    token_type: str = Field(
        'Bearer',
        title='令牌类型',
        description='令牌类型'
    )
    scope: str = Field(
        Required,
        title='范围',
        description='范围'
    )
    expires_in: int = Field(
        Required,
        title='过期时间',
        description='过期时间，单位：秒'
    )
    ext_expires_in: int = Field(
        Required,
        title='扩展过期时间',
        description='扩展过期时间，单位：秒'
    )
    access_token: str = Field(
        Required,
        title='访问令牌',
        description='访问令牌'
    )
    refresh_token: str = Field(
        Required,
        title='刷新令牌',
        description='刷新令牌'
    )
    id_token: str = Field(
        Required,
        title='标识令牌',
        description='标识令牌'
    )
    client_info: str = Field(
        Required,
        title='客户端信息',
        description='客户端信息'
    )
    id_token_claims: dict[str, str] = Field(
        Required,
        title='标识令牌声明',
        description='标识令牌声明'
    )


class GraphObject(BaseModel):
    odata_etag: str = Field(
        None,
        title='实体标记',
        description='ETag（实体标记）是符合HTTP/1.1标准的Web服务器返回的HTTP响应标头，用于确定给定URL处资源内容的更改'
    )
    id: str = Field(
        None,
        title='对象标识符',
        description='对象的唯一标识符'
    )


class WellKnownListName(str, Enum):
    none = 'none'  # 用户创建的列表
    defaultList = 'defaultList'  # 内置任务列表
    flaggedEmails = 'flaggedEmails'  # 内置的已标记电子邮件列表。此列表中存在标记电子邮件中的任务
    unknownFutureValue = 'unknownFutureValue'  # 可演变枚举sentinel值。请勿使用


class TodoTaskList(GraphObject):
    displayName: str = Field(
        None,
        title='任务列表名称',
        description='任务列表的名称'
    )
    isOwner: bool = Field(
        None,
        title='是拥有者',
        description='如果用户是给定任务列表的所有者，则为`True`'
    )
    isShared: bool = Field(
        None,
        title='是共享的',
        description='如果任务列表与其他用户共享，则为`True`'
    )
    wellknownListName: WellKnownListName = Field(
        None,
        title='已知列表',
        description='如果给定列表是已知列表，则指示列表名称的属性。可能的值是：`{}`、`{}`、`{}`、`{}`'.format(
            WellKnownListName.none,
            WellKnownListName.defaultList,
            WellKnownListName.flaggedEmails,
            WellKnownListName.unknownFutureValue
        )
    )

    class Config:
        schema_extra = {
            "example": {
                "odata_etag": "string",
                "id": "string",
                "displayName": "string",
                "isOwner": True,
                "isShared": True,
                "wellknownListName": WellKnownListName.none
            }
        }


class BodyType(str, Enum):
    text = 'text'
    html = 'html'


class ItemBody(BaseModel):
    content: str = Field(
        None,
        title='内容',
        description='项目的内容'
    )
    contentType: BodyType = Field(
        BodyType.text,
        title='内容类型',
        description='内容的类型。可能的值为`text`和`html`'
    )

    class Config:
        schema_extra = {
            "example": {
                "content": "string",
                "contentType": BodyType.text
            }
        }


class DateTimeTimeZone(BaseModel):
    dateTime: datetime | str = Field(
        Required,
        title='日期和时间',
        description='日期和时间组合表示形式的单个时间点（{date}T{time}；例如 2017-08-29T04:00:00.0000000）',
        example='2017-08-29T04:00:00.0000000'
    )
    timeZone: str = Field(
        'China Standard Time',
        title='时区',
        description='表示时区'
    )

    class Config:
        schema_extra = {
            "example": {
                "dateTime": "2020-01-01T00:00:00Z",
                "timeZone": "UTC"
            }
        }


class TodoTaskImportance(str, Enum):
    low = 'low'
    normal = 'normal'
    high = 'high'


class DayOfWeek(str, Enum):
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'


class RecurrencePatternType(str, Enum):
    daily = 'daily'
    weekly = 'weekly'
    absoluteMonthly = 'absoluteMonthly'
    relativeMonthly = 'relativeMonthly'
    absoluteYearly = 'absoluteYearly'
    relativeYearly = 'relativeYearly'


class RecurrencePatternIndex(str, Enum):
    first = 'first'
    second = 'second'
    third = 'third'
    fourth = 'fourth'
    last = 'last'


class RecurrencePattern(BaseModel):
    dayOfMonth: int = Field(
        None,
        title='月中的日期',
        description='事件在相应月份的多少号发生。如果`type`为`{}`或`{}`，此为必需属性'.format(
            RecurrencePatternType.absoluteMonthly,
            RecurrencePatternType.absoluteYearly
        )
    )
    daysOfWeek: list[DayOfWeek] = Field(
        None,
        title='星期几',
        description='''事件在星期几（一系列值）发生。可取值包括：`{}`、`{}`、`{}`、`{}`、`{}`、`{}`、`{}`。
如果`type`为`{}`或`{}`，且`daysOfWeek`指定超过一天，事件遵循相应模式的第一天规则。如果`type`为`{}`、`{}`或`{}`，此为必需属性。'''.format(
            DayOfWeek.monday, DayOfWeek.tuesday, DayOfWeek.wednesday, DayOfWeek.thursday, DayOfWeek.friday,
            DayOfWeek.saturday, DayOfWeek.sunday, RecurrencePatternType.relativeMonthly,
            RecurrencePatternType.relativeYearly, RecurrencePatternType.weekly, RecurrencePatternType.relativeMonthly,
            RecurrencePatternType.relativeYearly
        )
    )
    firstDayOfWeek: DayOfWeek = Field(
        None,
        title='周的第一天',
        description='星期几。可能的值为`{}`、`{}`、`{}`、`{}`、`{}`、`{}`和`{}`。如果`type`为`{}`，此为必需属性。'.format(
            DayOfWeek.monday, DayOfWeek.tuesday, DayOfWeek.wednesday, DayOfWeek.thursday, DayOfWeek.friday,
            DayOfWeek.saturday, DayOfWeek.sunday, RecurrencePatternType.weekly
        )
    )
    index: str = Field(
        None,
        title='索引',
        description='''指定事件发生在`daysOfWeek`中指定的允许天数实例的哪个实例上，从当月的第一个实例计数。
可能的值包括`{}`、`{}`、`{}`、`{}`、`{}`。默认值为`{}`。如果`type`为`{}`或`{}`，请使用此可选属性。'''.format(
            RecurrencePatternIndex.first, RecurrencePatternIndex.second, RecurrencePatternIndex.third,
            RecurrencePatternIndex.fourth, RecurrencePatternIndex.last, RecurrencePatternIndex.first,
            RecurrencePatternType.relativeMonthly, RecurrencePatternType.relativeYearly
        )
    )
    interval: int = Field(
        None,
        title='间隔',
        description='间隔的单元数，可以是天数、周数、月数或年数，具体视`type`而定。此为必需属性。'
    )
    month: int = Field(
        None,
        title='月份',
        description='事件发生的月份。这是一个介于`1`到`12`之间的数字。'
    )
    type: RecurrencePatternType = Field(
        Required,
        title='类型',
        description='必填。定期模式类型：`{}`、`{}`、`{}`、`{}`、`{}`或`{}`'.format(
            RecurrencePatternType.daily, RecurrencePatternType.weekly, RecurrencePatternType.absoluteMonthly,
            RecurrencePatternType.relativeMonthly, RecurrencePatternType.absoluteYearly,
            RecurrencePatternType.relativeYearly
        )
    )


class RecurrenceRangeType(str, Enum):
    endDate = 'endDate'
    noEnd = 'noEnd'
    numbered = 'numbered'


class RecurrenceRange(BaseModel):
    endDate: date | str = Field(
        None,
        title='停止应用日期',
        description='定期模式的停止应用日期。会议的最后一次发生时间可能不是此日期，具体视事件的定期模式而定。'
                    '如果`type`为`{}`，此为必需属性。'.format(RecurrenceRangeType.endDate)
    )
    numberOfOccurrences: int = Field(
        None,
        title='重复次数',
        description='事件重复发生次数。如果`type`为`{}`，此为必需属性。'.format(RecurrenceRangeType.numbered)
    )
    recurrenceTimeZone: str = Field(
        None,
        title='重复时区',
        description='`startDate`和`endDate`属性的时区。此为可选属性。如果未指定，使用的是事件时区'
    )
    startDate: date | str = Field(
        None,
        title='开始日期',
        description='定期模式的开始应用日期。会议的第一次发生时间可能是此日期，也可能晚于此日期，具体视事件的定期模式而定。'
                    '必须与定期事件的`start`属性值相同。此为必需属性。'
    )
    type: RecurrenceRangeType = Field(
        Required,
        title='类型',
        description='必填。定期范围类型：`{}`、`{}`或`{}`'.format(
            RecurrenceRangeType.endDate, RecurrenceRangeType.noEnd, RecurrenceRangeType.numbered
        )
    )


class PatternedRecurrence(BaseModel):
    pattern: RecurrencePattern = Field(
        Required,
        title='重复模式',
        description='指定重复模式的属性'
    )
    range: RecurrenceRange = Field(
        Required,
        title='重复范围',
        description='指定重复范围的属性'
    )


class TodoTaskStatus(str, Enum):
    notStarted = 'notStarted'
    inProgress = 'inProgress'
    completed = 'completed'
    waitingOnOthers = 'waitingOnOthers'
    deferred = 'deferred'


class TodoTask(GraphObject):
    body: ItemBody = Field(
        None,
        title='正文',
        description='通常包含有关任务的信息的任务正文'
    )
    bodyLastModifiedDateTime: datetime | str = Field(
        None,
        title='上次修改任务正文的日期和时间',
        description='上次修改任务正文的日期和时间。默认情况下，它采用UTC格式。属性值使用ISO8601格式，并始终处于UTC时间',
        example='2020-01-01T00:00:00Z'
    )
    categories: list[str] = Field(
        None,
        title='类别',
        description='与任务关联的类别。 每个类别对应于用户定义的`outlookCategory`的`displayName`属性'
    )
    completedDateTime: DateTimeTimeZone = Field(
        None,
        title='完成日期和时间',
        description='任务完成的指定时区中的日期和时间'
    )
    createdDateTime: datetime | str = Field(
        None,
        title='任务的创建日期和时间',
        description='任务的创建日期和时间。默认情况下，它采用UTC格式。属性值使用ISO8601格式，并始终处于UTC时间',
        example='2020-01-01T00:00:00Z'
    )
    dueDateTime: DateTimeTimeZone = Field(
        None,
        title='截止日期和时间',
        description='任务的指定时区中的截止日期和时间'
    )
    hasAttachments: bool = Field(
        None,
        title='是否有附件',
        description='指示任务是否具有附件'
    )
    importance: TodoTaskImportance = Field(
        None,
        title='重要性',
        description='任务的重要性。可取值为：`{}`、`{}`、`{}`'.format(
            TodoTaskImportance.low, TodoTaskImportance.normal, TodoTaskImportance.high
        )
    )
    isReminderOn: bool = Field(
        None,
        title='是否提醒',
        description='如果设置警报以提醒用户有任务，则设置为`true`'
    )
    lastModifiedDateTime: datetime | str = Field(
        None,
        title='上次修改任务的日期和时间',
        description='上次修改任务的日期和时间。默认情况下，它采用UTC格式。属性值使用ISO8601格式，并始终处于UTC时间'
    )
    recurrence: PatternedRecurrence = Field(
        None,
        title='定期模式',
        description='任务的定期模式。'
    )
    reminderDateTime: DateTimeTimeZone = Field(
        None,
        title='提醒日期和时间',
        description='指定时区中要发生的任务的提醒警报的日期和时间'
    )
    startDateTime: DateTimeTimeZone = Field(
        None,
        title='开始日期和时间',
        description='计划任务开始的指定时区中的日期和时间'
    )
    status: TodoTaskStatus = Field(
        None,
        title='状态',
        description='指示任务的状态或进度。可取值为：`{}`、`{}`、`{}`、`{}`、`{}`'.format(
            TodoTaskStatus.notStarted, TodoTaskStatus.inProgress, TodoTaskStatus.completed,
            TodoTaskStatus.waitingOnOthers, TodoTaskStatus.deferred
        )
    )
    title: str = Field(
        None,
        title='标题',
        description='任务的简要说明'
    )


class TaskFileAttachment(GraphObject):
    contentBytes: bytes = Field(
        None,
        title='内容字节',
        description='文件的Base64编码内容'
    )
    contentType: str = Field(
        None,
        title='内容类型',
        description='附件的内容类型'
    )
    lastModifiedDateTime: datetime | str = Field(
        None,
        title='上次修改日期和时间',
        description='上次修改附件的日期和时间',
        example='2020-01-01T00:00:00Z'
    )
    name: str = Field(
        None,
        title='名称',
        description='表示嵌入附件的图标下显示的文本的名称。这不必是实际的文件名'
    )
    size: int = Field(
        None,
        title='附件大小',
        description='附件大小，以字节为单位'
    )


class AttachmentType(str, Enum):
    file = 'file'
    item = 'item'
    reference = 'reference'


class AttachmentInfo(BaseModel):
    attachmentType: AttachmentType = Field(
        AttachmentType.file,
        title='附件类型',
        description='附件的类型。可能的值包括：`{}`、`{}`、`{}`'.format(
            AttachmentType.file, AttachmentType.item, AttachmentType.reference
        )
    )
    contentType: str = Field(
        None,
        title='内容类型',
        description='附件中数据的性质'
    )
    name: str = Field(
        Required,
        title='名称',
        description='附件的显示名称。这可以是描述性字符串，不一定是实际文件名'
    )
    size: int = Field(
        Required,
        title='附件大小',
        description='附件大小，以字节为单位，不能超过25MB，即26,214,400字节',
        lt=26214400
    )


class UploadSession(BaseModel):
    expirationDateTime: datetime | str = Field(
        Required,
        title='过期日期和时间',
        description='以UTC表示的上载会话过期的日期和时间。在此过期时间之前必须上载完整的文件文件',
        example='2020-01-01T00:00:00Z'
    )
    nextExpectedRanges: list[str] = Field(
        Required,
        title='下一步预期范围',
        description='字节范围集合，服务器缺失的文件。这些区域索引均从零开始，格式为"开始-结束"（例如，"0-26"指示该文件的前27个字节)。'
                    '将文件作为Outlook附件上传时，此属性始终指示单个值“{start}”，而不是范围集合，即文件中应开始下一次上传的位置。'
    )
    uploadUrl: str = Field(
        Required,
        title='上传URL',
        description='接受文件字节范围的PUT请求的URL端点'
    )


class CheckListItem(GraphObject):
    checkedDateTime: datetime | str = Field(
        None,
        title='完成日期和时间',
        description='清单项完成的日期和时间',
        example='2020-01-01T00:00:00Z'
    )
    createdDateTime: datetime | str = Field(
        None,
        title='创建日期和时间',
        description='创建清单项的日期和时间',
        example='2020-01-01T00:00:00Z'
    )
    displayName: str = Field(
        None,
        title='标题',
        description='指示`checklistItem`标题的字段'
    )
    isChecked: bool = Field(
        None,
        title='是否已完成',
        description='指示是否签出项的状态'
    )


class LinkedResource(GraphObject):
    applicationName: str = Field(
        None,
        title='应用程序名称',
        description='发送`linkedResource`的源的应用名称'
    )
    displayName: str = Field(
        None,
        title='标题',
        description='`linkedResource`的标题'
    )
    externalId: str = Field(
        None,
        title='外部ID',
        description='与第三方/合作伙伴系统上的此任务关联的对象的ID'
    )
    webUrl: HttpUrl | str = Field(
        None,
        title='Web URL',
        description='指向`linkedResource`的深层链接'
    )
