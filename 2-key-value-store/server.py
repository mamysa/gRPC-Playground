import grpc
import kv_store_pb2
import kv_store_pb2_grpc
from concurrent import futures
import time
from threading import Lock

class KeyValueStoreImpl(kv_store_pb2_grpc.KeyValueStoreServiceServicer):

    def __init__(self):
        self.mutex = Lock()
        self.store = {} 



    def put_value(self, request, context):
        self.mutex.acquire()
        try:
            self.store[request.key] = request.value
        finally:
            self.mutex.release()
        status = kv_store_pb2.KeyValueResult.Value('OK')
        return kv_store_pb2.Value(status=status, value=request.value)

    def get_value(self, request, context):
        self.mutex.acquire()
        try:
            val = self.store[request.key] 
            status = kv_store_pb2.KeyValueResult.Value('OK')
        except KeyError:
            val = 0;
            status = kv_store_pb2.KeyValueResult.Value('UNKNOWN_KEY')
        finally:
            self.mutex.release()
        return kv_store_pb2.Value(status=status, value=val)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))#, maximum_concurrent_rpcs=2)
    server.add_insecure_port('[::]:50051')
    kv_store_pb2_grpc.add_KeyValueStoreServiceServicer_to_server(KeyValueStoreImpl(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
