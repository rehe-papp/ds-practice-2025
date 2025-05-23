from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class DatabasePrepareRequest(_message.Message):
    __slots__ = ("order_id", "item_updates")
    class ItemUpdate(_message.Message):
        __slots__ = ("title", "quantity_change")
        TITLE_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_CHANGE_FIELD_NUMBER: _ClassVar[int]
        title: str
        quantity_change: int
        def __init__(self, title: _Optional[str] = ..., quantity_change: _Optional[int] = ...) -> None: ...
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_UPDATES_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    item_updates: _containers.RepeatedCompositeFieldContainer[DatabasePrepareRequest.ItemUpdate]
    def __init__(self, order_id: _Optional[int] = ..., item_updates: _Optional[_Iterable[_Union[DatabasePrepareRequest.ItemUpdate, _Mapping]]] = ...) -> None: ...

class DatabasePrepareResponse(_message.Message):
    __slots__ = ("ready",)
    READY_FIELD_NUMBER: _ClassVar[int]
    ready: bool
    def __init__(self, ready: bool = ...) -> None: ...

class DatabaseCommitRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    def __init__(self, order_id: _Optional[int] = ...) -> None: ...

class DatabaseCommitResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DatabaseAbortRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    def __init__(self, order_id: _Optional[int] = ...) -> None: ...

class DatabaseAbortResponse(_message.Message):
    __slots__ = ("aborted",)
    ABORTED_FIELD_NUMBER: _ClassVar[int]
    aborted: bool
    def __init__(self, aborted: bool = ...) -> None: ...
