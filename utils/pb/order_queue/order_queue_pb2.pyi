from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BookItem(_message.Message):
    __slots__ = ("title", "quantity")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    title: str
    quantity: int
    def __init__(self, title: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("orderId", "userName", "items")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    orderId: int
    userName: str
    items: _containers.RepeatedCompositeFieldContainer[BookItem]
    def __init__(self, orderId: _Optional[int] = ..., userName: _Optional[str] = ..., items: _Optional[_Iterable[_Union[BookItem, _Mapping]]] = ...) -> None: ...

class EnqueueRequest(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class EnqueueResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DequeueRequest(_message.Message):
    __slots__ = ("executor_id",)
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    executor_id: int
    def __init__(self, executor_id: _Optional[int] = ...) -> None: ...

class DequeueResponse(_message.Message):
    __slots__ = ("success", "order")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    success: bool
    order: Order
    def __init__(self, success: bool = ..., order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...
