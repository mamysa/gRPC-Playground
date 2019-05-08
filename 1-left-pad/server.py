import grpc
import left_pad_pb2
import left_pad_pb2_grpc
from concurrent import futures
import time

class LeftPadImpl(left_pad_pb2_grpc.LeftPadServiceServicer):
    def left_pad(self, request, context):
        #context.abort(grpc.StatusCode.INVALID_ARGUMENT, "oh no something went wrong")
        ch = ' ' if len(request.ch) == 0 else request.ch
        print( 'Received string={}'.format(request.string_to_pad) )
        padded = ch * request.len + request.string_to_pad
        return left_pad_pb2.LeftPadOutput(result=padded)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))#, maximum_concurrent_rpcs=2)
    server.add_insecure_port('[::]:50051')
    left_pad_pb2_grpc.add_LeftPadServiceServicer_to_server(LeftPadImpl(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
