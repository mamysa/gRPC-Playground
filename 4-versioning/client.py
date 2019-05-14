import grpc
import kv_store_v2_pb2
import kv_store_v2_pb2_grpc
import logging
import time
import argparse

def put_value(stub, key, val1, val2, operator):
    args = kv_store_v2_pb2.PutValueInput(key=key, val1=val1, val2=val2, op=operator)
    response = stub.put_value(args)
    return response.value

def get_value(stub, key):
    args = kv_store_v2_pb2.GetValueInput(key=key)
    response = stub.get_value(args)
    return response.value

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = kv_store_v2_pb2_grpc.KeyValueStoreServiceStub(channel)
        try:
            if args.put:
                op = kv_store_v2_pb2.ASSIGN
                if args.add: op = kv_store_v2_pb2.ADD
                if args.mul: op = kv_store_v2_pb2.MUL
                key = args.key; val1 = args.val1; val2 = args.val2; 
                assert key != None and val1 != None
                print( put_value(stub, key, val1, val2, op) )
            elif args.get:
                key = args.key; assert key != None
                print( get_value(stub, key) )
        except grpc.RpcError as e:
            print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--put', action='store_true', help='Put key-value into key-value store' )
    parser.add_argument('--get', action='store_true', help='Get value from key-value store' )
    parser.add_argument('-key', type=str)
    parser.add_argument('-val1', type=int)
    parser.add_argument('-val2', type=int, default=0)
    parser.add_argument('--add', action='store_true')
    parser.add_argument('--mul', action='store_true')
    args = parser.parse_args()
    run()
