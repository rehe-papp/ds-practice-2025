from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VectorClock(_message.Message):
    __slots__ = ("clock",)
    class ClockEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    clock: _containers.ScalarMap[str, int]
    def __init__(self, clock: _Optional[_Mapping[str, int]] = ...) -> None: ...

class SuggestBooksRequest(_message.Message):
    __slots__ = ("bookID", "vector_clock")
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    bookID: _containers.RepeatedScalarFieldContainer[int]
    vector_clock: VectorClock
    def __init__(self, bookID: _Optional[_Iterable[int]] = ..., vector_clock: _Optional[_Union[VectorClock, _Mapping]] = ...) -> None: ...

class BookSuggestion(_message.Message):
    __slots__ = ("bookID", "title", "author")
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    bookID: int
    title: str
    author: str
    def __init__(self, bookID: _Optional[int] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class SuggestionsResponse(_message.Message):
    __slots__ = ("suggestions", "vector_clock")
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[BookSuggestion]
    vector_clock: VectorClock
    def __init__(self, suggestions: _Optional[_Iterable[_Union[BookSuggestion, _Mapping]]] = ..., vector_clock: _Optional[_Union[VectorClock, _Mapping]] = ...) -> None: ...
