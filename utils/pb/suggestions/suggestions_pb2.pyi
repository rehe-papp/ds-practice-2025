from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SuggestBooksRequest(_message.Message):
    __slots__ = ("bookID",)
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    bookID: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, bookID: _Optional[_Iterable[int]] = ...) -> None: ...

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
    __slots__ = ("suggestions",)
    SUGGESTIONS_FIELD_NUMBER: _ClassVar[int]
    suggestions: _containers.RepeatedCompositeFieldContainer[BookSuggestion]
    def __init__(self, suggestions: _Optional[_Iterable[_Union[BookSuggestion, _Mapping]]] = ...) -> None: ...
