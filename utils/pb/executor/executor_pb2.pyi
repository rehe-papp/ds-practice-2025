from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HeartbeatRequest(_message.Message):
    __slots__ = ("from_executor_id",)
    FROM_EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    from_executor_id: int
    def __init__(self, from_executor_id: _Optional[int] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("alive",)
    ALIVE_FIELD_NUMBER: _ClassVar[int]
    alive: bool
    def __init__(self, alive: bool = ...) -> None: ...

class ElectionRequest(_message.Message):
    __slots__ = ("from_executor_id",)
    FROM_EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    from_executor_id: int
    def __init__(self, from_executor_id: _Optional[int] = ...) -> None: ...

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
