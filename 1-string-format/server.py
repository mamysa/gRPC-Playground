import grpc
import string_formatter_pb2
import string_formatter_pb2_grpc
from concurrent import futures
import time

class StringFormatterImpl():
    def formatInt(self, request, context):
        print('Received string={}, num0={}, num1={}, num2={}'.format(request.string_to_format, request.num0, request.num1, request.num2))
        if request.string_to_format.count('{}') != 3: 
            status = string_formatter_pb2.StringFormatterStatus.Value('FAILURE')
            print(status)
            return string_formatter_pb2.StringFormatterOutput(status=status)

        ret = request.string_to_format.format(request.num0, request.num1, request.num2)
        status = string_formatter_pb2.StringFormatterStatus.Value('SUCCESS')
        print(status, ret)
        return string_formatter_pb2.StringFormatterOutput(status=status, result=ret)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))#, maximum_concurrent_rpcs=2)
    server.add_insecure_port('[::]:50051')
    string_formatter_pb2_grpc.add_StringFormatterServiceServicer_to_server(StringFormatterImpl(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
