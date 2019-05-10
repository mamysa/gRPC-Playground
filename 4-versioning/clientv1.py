import grpc
import kv_store2_pb2
import kv_store2_pb2_grpc
import logging
import time

def put_value_int(stub, key, value):
    args = kv_store2_pb2.PutValueInput(key=key, value=value)
    response = stub.put_value(args)
    return response.value

def put_value_str(stub, key, string_value):
    args = kv_store2_pb2.PutValueInput(key=key, string_value=string_value)
    response = stub.put_value(args)
    return response.string_value


def get_value(stub, key):
    args = kv_store2_pb2.GetValueInput(key=key)
    response = stub.get_value(args)
    return response.value

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50055') as channel:
        stub = kv_store2_pb2_grpc.KeyValueStoreV1Stub(channel)
        try:
            print( put_value_int(stub, 'x', 12) )
            print( put_value_str(stub, 'y', 'Hello World!') )
        except grpc.RpcError as e:
            print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))
        except Exception as err:
            print(str(err))

if __name__ == '__main__':
    run()