import grpc
import kv_store2_pb2
import kv_store2_pb2_grpc
from concurrent import futures
import time
from threading import Lock
import os 

class KeyValueStoreImplV1(kv_store2_pb2_grpc.KeyValueStoreV1Servicer):
    def __init__(self):
        self.mutex = Lock()
        self.store = {} 

    def put_value(self, request, context):
        if len(request.string_value) != 0:
            self.mutex.acquire()
            try:
                self.store[request.key] = request.string_value
            finally:
                self.mutex.release()
            return kv_store2_pb2.Value(string_value=request.string_value)
        else: 
            self.mutex.acquire()
            try:
                self.store[request.key] = request.value
            finally:
                self.mutex.release()
            return kv_store2_pb2.Value(value=request.value)

    def get_value(self, request, context):
        self.mutex.acquire()
        try:
            val = self.store[request.key] 
            if isinstance(val, str):
                ret = kv_store2_pb2.Value(string_value=val)
            else:
                ret = kv_store2_pb2.Value(value=val)
        except KeyError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details( 'Invalid key {}'.format(request.key) )
            ret = kv_store2_pb2.Value()
        finally:
            self.mutex.release()
        return  ret

class KeyValueStoreImplV2(kv_store2_pb2_grpc.KeyValueStoreV2Servicer):
    def __init__(self):
        self.mutex = Lock()
        self.store = {} 

    def put_value(self, request, context):
        self.mutex.acquire()
        try:
            self.store[request.key] = request.value
        finally:
            self.mutex.release()
        return kv_store2_pb2.ValueV2(value=request.value)

    def get_value(self, request, context):
        self.mutex.acquire()
        try:
            val = self.store[request.key] 
            ret = kv_store2_pb2.ValueV2(value=val)
        except KeyError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details( 'Invalid key {}'.format(request.key) )
            ret = kv_store2_pb2.ValueV2()
        finally:
            self.mutex.release()
        return  ret

    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))#, maximum_concurrent_rpcs=1)
    server.add_insecure_port('[::]:50055')
    kv_store2_pb2_grpc.add_KeyValueStoreV1Servicer_to_server(KeyValueStoreImplV1(), server)
    kv_store2_pb2_grpc.add_KeyValueStoreV2Servicer_to_server(KeyValueStoreImplV2(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
