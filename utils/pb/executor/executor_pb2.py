# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: executor.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x65xecutor.proto\x12\x08\x65xecutor\",\n\x10HeartbeatRequest\x12\x18\n\x10\x66rom_executor_id\x18\x01 \x01(\x05\"\"\n\x11HeartbeatResponse\x12\r\n\x05\x61live\x18\x01 \x01(\x08\"+\n\x0f\x45lectionRequest\x12\x18\n\x10\x66rom_executor_id\x18\x01 \x01(\x05\"(\n\x10\x45lectionResponse\x12\x14\n\x0c\x61\x63knowledged\x18\x01 \x01(\x08\"+\n\x12\x43oordinatorMessage\x12\x15\n\rnew_leader_id\x18\x01 \x01(\x05\"\x07\n\x05\x45mpty2\xe4\x01\n\x0f\x45xecutorService\x12H\n\rSendHeartbeat\x12\x1a.executor.HeartbeatRequest\x1a\x1b.executor.HeartbeatResponse\x12\x46\n\rStartElection\x12\x19.executor.ElectionRequest\x1a\x1a.executor.ElectionResponse\x12?\n\x0e\x41nnounceLeader\x12\x1c.executor.CoordinatorMessage\x1a\x0f.executor.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'executor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_HEARTBEATREQUEST']._serialized_start=28
  _globals['_HEARTBEATREQUEST']._serialized_end=72
  _globals['_HEARTBEATRESPONSE']._serialized_start=74
  _globals['_HEARTBEATRESPONSE']._serialized_end=108
  _globals['_ELECTIONREQUEST']._serialized_start=110
  _globals['_ELECTIONREQUEST']._serialized_end=153
  _globals['_ELECTIONRESPONSE']._serialized_start=155
  _globals['_ELECTIONRESPONSE']._serialized_end=195
  _globals['_COORDINATORMESSAGE']._serialized_start=197
  _globals['_COORDINATORMESSAGE']._serialized_end=240
  _globals['_EMPTY']._serialized_start=242
  _globals['_EMPTY']._serialized_end=249
  _globals['_EXECUTORSERVICE']._serialized_start=252
  _globals['_EXECUTORSERVICE']._serialized_end=480
# @@protoc_insertion_point(module_scope)
