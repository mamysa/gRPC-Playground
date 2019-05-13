import grpc
import pgm_store_pb2 
import pgm_store_pb2_grpc 
import logging
import time
import ppm
import argparse

def write_image(stub, filename):
    image_data = ppm.load_image(filename)

    total_pixels = (len(image_data) - 4) // 3

    def send_pixel_data():
        ## ignore first 4 elements
        num_pixels = 1
        for i in range(4, len(image_data), 3):
            r = int(image_data[i+0])
            g = int(image_data[i+1])
            b = int(image_data[i+2])
            print('Send pixeldata {}/{}'.format(num_pixels, total_pixels))
            yield pgm_store_pb2.PixelData(r=r, g=g, b=b)
            num_pixels += 1

    # These go into the header.
    metadata = (('w', image_data[1]), 
                ('h', image_data[2]), 
                ('depth', image_data[3]),
                ('filename', filename))

    response = stub.write_image(send_pixel_data(), metadata=metadata)

def get_image(stub, filename):
    argument = pgm_store_pb2.GetImageInput(filename=filename)
    response = stub.get_image(argument)

    w = None; h = None; depth  = None;
    for key, value in response.initial_metadata():
        if key == 'w': w = value
        if key == 'h': h = value
        if key == 'depth': depth = value 
    
    if not w: raise Exception('missing w')
    if not h: raise Exception('missing h')
    if not depth: raise Exception('missing depth ')
    image_data = ['P3', w, h, depth]

    num_pixels = 1
    for rgb in response: 
        image_data.append(str(rgb.r))
        image_data.append(str(rgb.g))
        image_data.append(str(rgb.b))
        print('Received {}'.format(num_pixels))
        num_pixels += 1
    ppm.write_image('client_'+filename, image_data)

def greyscale(stub, filename):
    image_data = ppm.load_image(filename)

    total_pixels = (len(image_data) - 4) // 3
    def send_pixel_data():
        num_sent = 1
        ## ignore first 4 elements
        for i in range(4, len(image_data), 3):
            r = int(image_data[i+0])
            g = int(image_data[i+1])
            b = int(image_data[i+2])
            yield pgm_store_pb2.PixelData(r=r, g=g, b=b)
            print('Send pixeldata {}/{}'.format(num_sent, total_pixels))
            num_sent += 1

    response = stub.greyscale(send_pixel_data())
    new_image_data = [ image_data[0], image_data[1], image_data[2], image_data[3] ] 
    num_received = 1
    for rgb in response: 
        new_image_data.append(str(rgb.r))
        new_image_data.append(str(rgb.g))
        new_image_data.append(str(rgb.b))
        print('Received pixeldata {}/{}'.format(num_received, total_pixels))
        num_received += 1

    ppm.write_image('greyscale_'+filename, new_image_data)

def run():
    ## missing fields are replaced with default values
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pgm_store_pb2_grpc.PgmImageServiceStub(channel)
        try:
            pass
            if CLIARGS.send: write_image(stub, 'tux.ppm')
            if CLIARGS.recv: get_image(stub, 'tux.ppm')
            if CLIARGS.grey: greyscale(stub, 'tux.ppm')
        except grpc.RpcError as e:
            print('RpcError caught, code: {} details: {}'.format(e.code(), e.details()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--send', action='store_true', help='Send image')
    parser.add_argument('--recv', action='store_true', help='Receive image')
    parser.add_argument('--grey', action='store_true', help='Image 2 greyscale')
    CLIARGS = parser.parse_args()
    run()
