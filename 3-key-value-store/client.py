import grpc
import kv_store_pb2
import kv_store_pb2_grpc
import logging
import time
import argparse

def put_value(stub, key, value):
    args = kv_store_pb2.PutValueInput(key=key, value=value)
    response = stub.put_value(args)
    return response.value

def get_value(stub, key):
    args = kv_store_pb2.GetValueInput(key=key)
    response = stub.get_value(args)
    return response.value

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = kv_store_pb2_grpc.KeyValueStoreServiceStub(channel)
        try:
            if args.put:
                key = args.key; val = args.val
                assert key != None and val != None
                print( put_value(stub, key, val) )
            elif args.get:
                key = args.key
                assert key != None
                print( get_value(stub, key) )
        except grpc.RpcError as e:
            print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--put', action='store_true', help='Put key-value into key-value store' )
    parser.add_argument('--get', action='store_true', help='Get value from key-value store' )
    parser.add_argument('-key', type=str)
    parser.add_argument('-val', type=int)
    args = parser.parse_args()
    run()
