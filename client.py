import grpc
import streaming_pb2 
import streaming_pb2_grpc 

import logging
import time




def single_single_sync(channel):
    stub = streaming_pb2_grpc.NumberAdderStub(channel)
    response = stub.add_oneshot(streaming_pb2.TwoNumbers(lhs=4, rhs=12))  #timeout=4
    print(response.result)

def single_single_async(channel):
    def done(call_future):
        response = call_future.result()
        print('Single-Single Async response with result={}'.format(response.result))
    stub = streaming_pb2_grpc.NumberAdderStub(channel)
    call_future = stub.add_oneshot.future(streaming_pb2.TwoNumbers(lhs=4, rhs=13))
    call_future.add_done_callback(done)
    print('Sleeping for 10 seconds...')
    time.sleep(10)
    print('Done sleeping!')


def stream_single_sync(channel):
    def add_multiple():
        for x in range(4, 6):
            yield streaming_pb2.OneNumber(result=x) 

    stub = streaming_pb2_grpc.NumberAdderStub(channel)
    response = stub.add_stream_single(add_multiple())  #timeout=4
    print(response.result)


        
def stream_stream_sync(channel):
    def add_multiple():
        for x, y in zip(range(4, 9), range(9, 14)):
            msg = streaming_pb2.TwoNumbers(lhs=x, rhs=y)
            yield msg

    stub = streaming_pb2_grpc.NumberAdderStub(channel)
    responses = stub.add(add_multiple())  #timeout=4
    for response in responses:
        print(response.result)


def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50051') as channel:
        try:
            #single_single_sync(channel)
            #single_single_async(channel)
            #stream_stream_sync(channel)
            stream_single_sync(channel)

        except grpc.RpcError as e:
            print('oh no exception!')
            print(e.code(), e.details())


if __name__ == '__main__':
    run()
