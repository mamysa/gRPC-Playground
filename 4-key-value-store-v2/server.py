import grpc
import kv_store_v2_pb2
import kv_store_v2_pb2_grpc
from concurrent import futures
import time
from threading import Lock
import os 
import argparse


class KeyValueStoreImpl(kv_store_v2_pb2_grpc.KeyValueStoreServiceServicer):
    def __init__(self):
        self.mutex = Lock()
        self.store = {} 

    def put_value(self, request, context):
        val = request.val1;
        if request.op == kv_store_v2_pb2.ADD: val += request.val2
        if request.op == kv_store_v2_pb2.MUL: val *= request.val2

        self.mutex.acquire()
        print('Peer {} enters critical section with key={} val1={} val2={} op={}'.format(
            context.peer(), request.key, request.val1, request.val2, request.op))
        time.sleep(args.sleep)
        try:
            self.store[request.key] = val
        finally:
            self.mutex.release()
            print('Peer {} exits critical section'.format(context.peer()))
        return kv_store_v2_pb2.Value(value=val)

    def get_value(self, request, context):
        time.sleep(args.sleep)
        try:
            val = self.store[request.key] 
            ret = kv_store_v2_pb2.Value(value=val)
        except KeyError:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details( 'Invalid key {}'.format(request.key) )
            ret = kv_store_v2_pb2.Value()
        return  ret
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1), maximum_concurrent_rpcs=1)
    server.add_insecure_port('[::]:50051')
    kv_store_v2_pb2_grpc.add_KeyValueStoreServiceServicer_to_server(KeyValueStoreImpl(), server)
    server.start()
    print('Running KVStoreV2')
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-sleep', type=int, default=0, help='Sleep while client is in critical section (in seconds)')
    args = parser.parse_args()
    serve()
