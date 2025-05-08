from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ReadRequest(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ("stock", "timestamp")
    STOCK_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    stock: int
    timestamp: int
    def __init__(self, stock: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ("title", "new_stock", "timestamp")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    NEW_STOCK_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    title: str
    new_stock: int
    timestamp: int
    def __init__(self, title: _Optional[str] = ..., new_stock: _Optional[int] = ..., timestamp: _Optional[int] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ("from_database_id",)
    FROM_DATABASE_ID_FIELD_NUMBER: _ClassVar[int]
    from_database_id: int
    def __init__(self, from_database_id: _Optional[int] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("alive",)
    ALIVE_FIELD_NUMBER: _ClassVar[int]
    alive: bool
    def __init__(self, alive: bool = ...) -> None: ...

class ElectionRequest(_message.Message):
    __slots__ = ("from_database_id",)
    FROM_DATABASE_ID_FIELD_NUMBER: _ClassVar[int]
    from_database_id: int
    def __init__(self, from_database_id: _Optional[int] = ...) -> None: ...

class ElectionResponse(_message.Message):
    __slots__ = ("acknowledged",)
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    def __init__(self, acknowledged: bool = ...) -> None: ...

class CoordinatorMessage(_message.Message):
    __slots__ = ("new_leader_id",)
    NEW_LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    new_leader_id: int
    def __init__(self, new_leader_id: _Optional[int] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
