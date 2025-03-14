# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fraud_detection.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x66raud_detection.proto\x12\x0f\x66raud_detection\"%\n\x04User\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\"s\n\x0bVectorClock\x12\x36\n\x05\x63lock\x18\x01 \x03(\x0b\x32\'.fraud_detection.VectorClock.ClockEntry\x1a,\n\nClockEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\"A\n\nCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x16\n\x0e\x65xpirationDate\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t\"(\n\x04Item\x12\x0e\n\x06\x62ookid\x18\x01 \x01(\x03\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"T\n\x07\x41\x64\x64ress\x12\x0e\n\x06street\x18\x01 \x01(\t\x12\x0c\n\x04\x63ity\x18\x02 \x01(\t\x12\r\n\x05state\x18\x03 \x01(\t\x12\x0b\n\x03zip\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\"\xca\x02\n\x0c\x46raudRequest\x12#\n\x04user\x18\x01 \x01(\x0b\x32\x15.fraud_detection.User\x12/\n\ncreditCard\x18\x02 \x01(\x0b\x32\x1b.fraud_detection.CreditCard\x12\x13\n\x0buserComment\x18\x03 \x01(\t\x12$\n\x05items\x18\x04 \x03(\x0b\x32\x15.fraud_detection.Item\x12\x30\n\x0e\x62illingAddress\x18\x05 \x01(\x0b\x32\x18.fraud_detection.Address\x12\x16\n\x0eshippingMethod\x18\x06 \x01(\t\x12\x14\n\x0cgiftWrapping\x18\x07 \x01(\x08\x12\x15\n\rtermsAccepted\x18\x08 \x01(\x08\x12\x32\n\x0cvector_clock\x18\t \x01(\x0b\x32\x1c.fraud_detection.VectorClock\"f\n\rFraudResponse\x12\x10\n\x08is_valid\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x32\n\x0cvector_clock\x18\x03 \x01(\x0b\x32\x1c.fraud_detection.VectorClock2h\n\x15\x46raudDetectionService\x12O\n\x0e\x46raudDetection\x12\x1d.fraud_detection.FraudRequest\x1a\x1e.fraud_detection.FraudResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'fraud_detection_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_VECTORCLOCK_CLOCKENTRY']._options = None
  _globals['_VECTORCLOCK_CLOCKENTRY']._serialized_options = b'8\001'
  _globals['_USER']._serialized_start=42
  _globals['_USER']._serialized_end=79
  _globals['_VECTORCLOCK']._serialized_start=81
  _globals['_VECTORCLOCK']._serialized_end=196
  _globals['_VECTORCLOCK_CLOCKENTRY']._serialized_start=152
  _globals['_VECTORCLOCK_CLOCKENTRY']._serialized_end=196
  _globals['_CREDITCARD']._serialized_start=198
  _globals['_CREDITCARD']._serialized_end=263
  _globals['_ITEM']._serialized_start=265
  _globals['_ITEM']._serialized_end=305
  _globals['_ADDRESS']._serialized_start=307
  _globals['_ADDRESS']._serialized_end=391
  _globals['_FRAUDREQUEST']._serialized_start=394
  _globals['_FRAUDREQUEST']._serialized_end=724
  _globals['_FRAUDRESPONSE']._serialized_start=726
  _globals['_FRAUDRESPONSE']._serialized_end=828
  _globals['_FRAUDDETECTIONSERVICE']._serialized_start=830
  _globals['_FRAUDDETECTIONSERVICE']._serialized_end=934
# @@protoc_insertion_point(module_scope)
