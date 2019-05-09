import grpc
import kv_store_pb2
import kv_store_pb2_grpc
from concurrent import futures
import time
from threading import Lock
import os 

class KeyValueStoreImpl(kv_store_pb2_grpc.KeyValueStoreServiceServicer):
    def __init__(self):
        self.mutex = Lock()
        self.store = {} 

    def put_value(self, request, context):
        time.sleep(2)
        #os._exit(1)
        self.mutex.acquire()
        print('Enter critical section')
        time.sleep(2)
        #time.sleep(8)
        try:
            self.store[request.key] = request.value
        finally:
            self.mutex.release()

        print('Exit critical section')
        status = kv_store_pb2.KeyValueResult.Value('OK')
        return kv_store_pb2.Value(status=status, value=request.value)

    def get_value(self, request, context):
        time.sleep(4)
        self.mutex.acquire()
        try:
            val = self.store[request.key] 
            status = kv_store_pb2.KeyValueResult.Value('OK')
            ret = kv_store_pb2.Value(status=status, value=val)
        except KeyError:
            #raise Exception( 'Invalid key {}'.format(request.key) )
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details( 'Invalid key {}'.format(request.key) )
            ret = kv_store_pb2.Value()
        finally:
            self.mutex.release()
        return  ret
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2), maximum_concurrent_rpcs=1)
    server.add_insecure_port('[::]:50050')
    kv_store_pb2_grpc.add_KeyValueStoreServiceServicer_to_server(KeyValueStoreImpl(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
