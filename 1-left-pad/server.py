import grpc
import left_pad_pb2
import left_pad_pb2_grpc
from concurrent import futures
import time

class LeftPadImpl(left_pad_pb2_grpc.LeftPadServiceServicer):
    # Create new subclass that extends *Servicer class in *_pb2_grpc.py and 
    # implement it here.
    def left_pad(self, request, context):
        ch = ' ' if len(request.ch) == 0 else request.ch
        print( 'Received string={} from peer {}'.format(request.string_to_pad, context.peer()) )
        padded = ch * request.len + request.string_to_pad
        return left_pad_pb2.LeftPadOutput(result=padded)
    
def serve():
    # Create the server and assign a port. If there are no available threads to 
    # process the request, said request will be queued.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    server.add_insecure_port('localhost:50051')

    # Register service implementation.
    left_pad_pb2_grpc.add_LeftPadServiceServicer_to_server(LeftPadImpl(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
