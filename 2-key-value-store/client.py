import grpc
import kv_store_pb2
import kv_store_pb2_grpc
import logging
import time

def put_value(stub, key, value):
    args = kv_store_pb2.PutValueInput(key=key, value=value)
    response = stub.put_value(args)
    return response.value

def get_value(stub, key):
    args = kv_store_pb2.GetValueInput(key=key)
    response = stub.get_value(args)
    if response.status == kv_store_pb2.OK:
        return response.value
    raise Exception('Unknown key {}'.format(key))

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = kv_store_pb2_grpc.KeyValueStoreServiceStub(channel)
        try:
            print( get_value(stub, 'x') )
        except grpc.RpcError as e:
            print('oh no exception!')
            print(e.code(), e.details())
        except Exception as err:
            print(str(err))

if __name__ == '__main__':
    run()
