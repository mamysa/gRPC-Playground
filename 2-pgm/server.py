import grpc
import pgm_store_pb2
import pgm_store_pb2_grpc
from concurrent import futures
import time
from threading import Lock
import os 
import ppm

class PgmStoreImpl(pgm_store_pb2_grpc.PgmImageServiceServicer):
    def write_image(self, request_iterator, context):
        w = None 
        h = None 
        depth = None 
        filename = None 
        for key, value in context.invocation_metadata():
            print(key, value)
            if key == 'w': w = value
            if key == 'h': h = value
            if key == 'depth': depth = value 
            if key == 'filename': filename = value

        if not w: raise Exception('missing w')
        if not h: raise Exception('missing h')
        if not depth: raise Exception('missing depth ')
        if not filename: raise Exception('missing filename')

        image_data = ['P3', w, h, depth]
        for rgb in request_iterator:
            print(rgb)
            image_data.append(str(rgb.r))
            image_data.append(str(rgb.g))
            image_data.append(str(rgb.b))

        ppm.write_image('server_'+filename, image_data)
        return pgm_store_pb2.Empty()

    def get_image(self, request, context):
        filename = request.filename
        try:
            image_data = ppm.load_image('server_' + filename)
        except:
            raise Exception('No {} on server!'.format(filename))

        metadata = (('w', image_data[1]), 
                    ('h', image_data[2]), 
                    ('depth', image_data[3]))
        context.send_initial_metadata(metadata)

        for i in range(4, len(image_data), 3):
            r = int(image_data[i+0])
            g = int(image_data[i+1])
            b = int(image_data[i+2])
            yield pgm_store_pb2.PixelData(r=r, g=g, b=b)

        
    def greyscale(self, request_iterator, context):
        for rgb in request_iterator:
            avg = (rgb.r + rgb.g + rgb.b) // 3
            yield pgm_store_pb2.PixelData(r=avg, g=avg, b=avg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    server.add_insecure_port('[::]:50051')
    pgm_store_pb2_grpc.add_PgmImageServiceServicer_to_server(PgmStoreImpl(), server)
    server.start()
    try:
        while True:
            time.sleep(4000)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
