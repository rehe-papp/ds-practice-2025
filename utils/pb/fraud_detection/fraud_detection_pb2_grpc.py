# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import fraud_detection_pb2 as fraud__detection__pb2


class FraudDetectionServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitializeFraud = channel.unary_unary(
                '/fraud_detection.FraudDetectionService/InitializeFraud',
                request_serializer=fraud__detection__pb2.FraudRequest.SerializeToString,
                response_deserializer=fraud__detection__pb2.FraudResponse.FromString,
                )
        self.ProcessFraud = channel.unary_unary(
                '/fraud_detection.FraudDetectionService/ProcessFraud',
                request_serializer=fraud__detection__pb2.ProcessFraudRequest.SerializeToString,
                response_deserializer=fraud__detection__pb2.FraudResponse.FromString,
                )
        self.ClearData = channel.unary_unary(
                '/fraud_detection.FraudDetectionService/ClearData',
                request_serializer=fraud__detection__pb2.ClearDataRequest.SerializeToString,
                response_deserializer=fraud__detection__pb2.ClearDataResponse.FromString,
                )


class FraudDetectionServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitializeFraud(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ProcessFraud(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ClearData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FraudDetectionServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InitializeFraud': grpc.unary_unary_rpc_method_handler(
                    servicer.InitializeFraud,
                    request_deserializer=fraud__detection__pb2.FraudRequest.FromString,
                    response_serializer=fraud__detection__pb2.FraudResponse.SerializeToString,
            ),
            'ProcessFraud': grpc.unary_unary_rpc_method_handler(
                    servicer.ProcessFraud,
                    request_deserializer=fraud__detection__pb2.ProcessFraudRequest.FromString,
                    response_serializer=fraud__detection__pb2.FraudResponse.SerializeToString,
            ),
            'ClearData': grpc.unary_unary_rpc_method_handler(
                    servicer.ClearData,
                    request_deserializer=fraud__detection__pb2.ClearDataRequest.FromString,
                    response_serializer=fraud__detection__pb2.ClearDataResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'fraud_detection.FraudDetectionService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FraudDetectionService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InitializeFraud(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/fraud_detection.FraudDetectionService/InitializeFraud',
            fraud__detection__pb2.FraudRequest.SerializeToString,
            fraud__detection__pb2.FraudResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ProcessFraud(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/fraud_detection.FraudDetectionService/ProcessFraud',
            fraud__detection__pb2.ProcessFraudRequest.SerializeToString,
            fraud__detection__pb2.FraudResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ClearData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/fraud_detection.FraudDetectionService/ClearData',
            fraud__detection__pb2.ClearDataRequest.SerializeToString,
            fraud__detection__pb2.ClearDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
