import grpc
import left_pad_pb2
import left_pad_pb2_grpc
import logging
import time
import argparse

def left_pad(channel, string_to_pad, length=0, ch=' '):
    stub = left_pad_pb2_grpc.LeftPadServiceStub(channel)
    args = left_pad_pb2.LeftPadInput(string_to_pad=string_to_pad, len=length, ch=ch)
    response = stub.left_pad(args)    #timeout=4
    return response.result

def run():
    ## missing fields are replaced with default values
    if args.multi:
        with grpc.insecure_channel('localhost:50051') as channel1,\
             grpc.insecure_channel('localhost:50052') as channel2:
            try:
                print( left_pad(channel1, 'pad me!', 4, ' ' ) )
                print( left_pad(channel2, 'pad me with zeros!!', 5, '0') )
            except grpc.RpcError as e:
                print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))
    else:
        with grpc.insecure_channel('localhost:50051') as channel:
            try:
                print( left_pad(channel, 'pad me!', 4, ' ' ) )
                print( left_pad(channel, 'pad me with zeros!!', 5, '0') )
            except grpc.RpcError as e:
                print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--multi', action='store_true', help='Establish connection two two servers listening on ports 50051 and 50052')
    args = parser.parse_args()
    run()
