# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import database_pb2 as database__pb2


class DatabaseServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Read = channel.unary_unary(
                '/database.DatabaseService/Read',
                request_serializer=database__pb2.ReadRequest.SerializeToString,
                response_deserializer=database__pb2.ReadResponse.FromString,
                )
        self.Write = channel.unary_unary(
                '/database.DatabaseService/Write',
                request_serializer=database__pb2.WriteRequest.SerializeToString,
                response_deserializer=database__pb2.WriteResponse.FromString,
                )
        self.SendHeartbeat = channel.unary_unary(
                '/database.DatabaseService/SendHeartbeat',
                request_serializer=database__pb2.HeartbeatRequest.SerializeToString,
                response_deserializer=database__pb2.HeartbeatResponse.FromString,
                )
        self.StartElection = channel.unary_unary(
                '/database.DatabaseService/StartElection',
                request_serializer=database__pb2.ElectionRequest.SerializeToString,
                response_deserializer=database__pb2.ElectionResponse.FromString,
                )
        self.AnnounceLeader = channel.unary_unary(
                '/database.DatabaseService/AnnounceLeader',
                request_serializer=database__pb2.CoordinatorMessage.SerializeToString,
                response_deserializer=database__pb2.Empty.FromString,
                )
        self.Prepare = channel.unary_unary(
                '/database.DatabaseService/Prepare',
                request_serializer=database__pb2.DatabasePrepareRequest.SerializeToString,
                response_deserializer=database__pb2.DatabasePrepareResponse.FromString,
                )
        self.Commit = channel.unary_unary(
                '/database.DatabaseService/Commit',
                request_serializer=database__pb2.DatabaseCommitRequest.SerializeToString,
                response_deserializer=database__pb2.DatabaseCommitResponse.FromString,
                )
        self.Abort = channel.unary_unary(
                '/database.DatabaseService/Abort',
                request_serializer=database__pb2.DatabaseAbortRequest.SerializeToString,
                response_deserializer=database__pb2.DatabaseAbortResponse.FromString,
                )


class DatabaseServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Read(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Write(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendHeartbeat(self, request, context):
        """Heartbeat message for leader liveness
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartElection(self, request, context):
        """Election message to start election
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AnnounceLeader(self, request, context):
        """Notification that a new leader is chosen
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Prepare(self, request, context):
        """Two-Phase Commit Methods
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Commit(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Abort(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DatabaseServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Read': grpc.unary_unary_rpc_method_handler(
                    servicer.Read,
                    request_deserializer=database__pb2.ReadRequest.FromString,
                    response_serializer=database__pb2.ReadResponse.SerializeToString,
            ),
            'Write': grpc.unary_unary_rpc_method_handler(
                    servicer.Write,
                    request_deserializer=database__pb2.WriteRequest.FromString,
                    response_serializer=database__pb2.WriteResponse.SerializeToString,
            ),
            'SendHeartbeat': grpc.unary_unary_rpc_method_handler(
                    servicer.SendHeartbeat,
                    request_deserializer=database__pb2.HeartbeatRequest.FromString,
                    response_serializer=database__pb2.HeartbeatResponse.SerializeToString,
            ),
            'StartElection': grpc.unary_unary_rpc_method_handler(
                    servicer.StartElection,
                    request_deserializer=database__pb2.ElectionRequest.FromString,
                    response_serializer=database__pb2.ElectionResponse.SerializeToString,
            ),
            'AnnounceLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.AnnounceLeader,
                    request_deserializer=database__pb2.CoordinatorMessage.FromString,
                    response_serializer=database__pb2.Empty.SerializeToString,
            ),
            'Prepare': grpc.unary_unary_rpc_method_handler(
                    servicer.Prepare,
                    request_deserializer=database__pb2.DatabasePrepareRequest.FromString,
                    response_serializer=database__pb2.DatabasePrepareResponse.SerializeToString,
            ),
            'Commit': grpc.unary_unary_rpc_method_handler(
                    servicer.Commit,
                    request_deserializer=database__pb2.DatabaseCommitRequest.FromString,
                    response_serializer=database__pb2.DatabaseCommitResponse.SerializeToString,
            ),
            'Abort': grpc.unary_unary_rpc_method_handler(
                    servicer.Abort,
                    request_deserializer=database__pb2.DatabaseAbortRequest.FromString,
                    response_serializer=database__pb2.DatabaseAbortResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'database.DatabaseService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class DatabaseService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Read(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/Read',
            database__pb2.ReadRequest.SerializeToString,
            database__pb2.ReadResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Write(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/Write',
            database__pb2.WriteRequest.SerializeToString,
            database__pb2.WriteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendHeartbeat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/SendHeartbeat',
            database__pb2.HeartbeatRequest.SerializeToString,
            database__pb2.HeartbeatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StartElection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/StartElection',
            database__pb2.ElectionRequest.SerializeToString,
            database__pb2.ElectionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AnnounceLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/AnnounceLeader',
            database__pb2.CoordinatorMessage.SerializeToString,
            database__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Prepare(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/Prepare',
            database__pb2.DatabasePrepareRequest.SerializeToString,
            database__pb2.DatabasePrepareResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Commit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/Commit',
            database__pb2.DatabaseCommitRequest.SerializeToString,
            database__pb2.DatabaseCommitResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Abort(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.DatabaseService/Abort',
            database__pb2.DatabaseAbortRequest.SerializeToString,
            database__pb2.DatabaseAbortResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
