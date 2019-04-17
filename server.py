import grpc
import streaming_pb2 
import streaming_pb2_grpc 

from concurrent import futures
import time

class NumberAdder(streaming_pb2_grpc.NumberAdderServicer):
    def add(self, request_iterator, context):
        result = 0
        for request in request_iterator:
            print(request.lhs, request.rhs)
            result += request.lhs * request.rhs
            yield streaming_pb2.OneNumber(result=result)
            time.sleep(1)

    def add_oneshot(self, request, context):
        time.sleep(2)
        result = request.lhs + request.rhs
        print('add_oneshot lhs={} rhs={} result={}'.format(request.lhs, request.rhs, result))
        return streaming_pb2.OneNumber(result=result)

    def add_stream_single(self, request_iterator, context):
        result = 0

        for request in request_iterator:
            print('Received number {}'.format(request.result))
            result += request.result
        return streaming_pb2.OneNumber(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2), maximum_concurrent_rpcs=2)
    streaming_pb2_grpc.add_NumberAdderServicer_to_server(NumberAdder(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
