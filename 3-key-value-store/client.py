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
    return response.value

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50050') as channel:
        stub = kv_store_pb2_grpc.KeyValueStoreServiceStub(channel)
        try:
            print( put_value(stub, 'x', 12) )
        except grpc.RpcError as e:
            print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))
        except Exception as err:
            print(str(err))

if __name__ == '__main__':
    run()
