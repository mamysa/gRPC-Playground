import grpc
import left_pad_pb2
import left_pad_pb2_grpc
import logging
import time

def left_pad(channel, string_to_pad, length=0, ch=' '):
    stub = left_pad_pb2_grpc.LeftPadServiceStub(channel)
    args = left_pad_pb2.LeftPadInput(string_to_pad=string_to_pad, len=length, ch=ch)
    response = stub.left_pad(args)#timeout=4
    return response.result

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50051') as channel:
        try:
            print( left_pad(channel, 'pad me!', 4, '0') )
        except grpc.RpcError as e:
            print('oh no exception!')
            print(e.code(), e.details())

if __name__ == '__main__':
    run()
