# gRPC Playground
gRPC is a remote procedure call framework developed by Google. It uses protobuf (protocol buffers) as interface definition language (by default) and uses HTTP/2 protocol for exchanging messages (i.e. binary protocol and allows for multiplexing (multiple requests can be served through single TCP connection). gRPC supports many different programming languages such as Java/C++/Python, etc.

1. Specify data types and services using specification language.
2. Compile specification into language of choice.  
3. Implement functionality behind the interface. 
4. Call desired interface. 
5. ???
6. Profit!




# Example 1 - Left Pad 

Example of single message in - single message out RPC. Relevant files for this are located in `1-left-pad directory`.

## Declaring RPC

`left_pad.proto` file contains RPC function declaration, definitions of an input message and output message. 

```
service LeftPadService {
	rpc left_pad(LeftPadInput) returns (LeftPadOutput) { }
}

message LeftPadInput {
	string string_to_pad = 1;
	uint32 len = 2;
	string ch = 3;
}

message LeftPadOutput {
	string result = 1;

}
```

In the example above, `LeftPadService` contains a single procedure that takes message of type `LeftPadInput` and returns `LeftPadOutput`. Messages can be composed of various primitive types such as `int32`, `float`, `string` as well as other messages. Each field in the message has a unique number that is used to identify fields a message when it is serialized. It is not necessary to assign values to every field - if certain field is missing in serialized message a default value will be assigned to it. Default values specific to each type.


References for this section -- 

https://developers.google.com/protocol-buffers/docs/proto3#services
https://developers.google.com/protocol-buffers/docs/proto3#default


## Compiling .proto
`*.proto` file can be compiled as follows: 
``` 
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. left_pad.proto`
```

Two files will be generated. `left_pad_pb2.py` defines all data types (and in case of Python it's not particularly readable...); `left_pad_pb2_grpc.py` defines  1. the stub for client to call (`LeftPadServiceStub`) and 2. `LeftPadServiceServicer` which is used implement desired RPC functionality.

## Server Implementation
Server functionality can be seen in `server.py`.

First, implement `left_pad` procedure by subclassing `LeftPadServiceServicer` class found in `left_pad_pb2_grpc.py`.

```
class LeftPadImpl(left_pad_pb2_grpc.LeftPadServiceServicer):
    def left_pad(self, request, context):
        ch = ' ' if len(request.ch) == 0 else request.ch
        print( 'Received string={} from peer {}'.format(request.string_to_pad, context.peer()) )
        padded = ch * request.len + request.string_to_pad
        return left_pad_pb2.LeftPadOutput(result=padded)
```

The server itself is created in the following way.  

```
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
server.add_insecure_port('localhost:50051')
left_pad_pb2_grpc.add_LeftPadServiceServicer_to_server(LeftPadImpl(), server)
server.start()
```

Line by line breakdown:

1. Create `grpc.server` object. `grpc.server` requires only one argument of type `ThreadPoolExecutor` which creates worker threads that handle procedure calls. In case if all worker threads are busy, new requests will be queued.
2. Created server should listen to specified port. Since port is `insecure`; clients do not require authentication to be able to call the procedure.
3. Provide instance of a class that actually implements desired RPC functionality. 
4. Finally, start the server. Procedure returns right away so something like `sleep` should be used to keep the server alive. 

## Client Implementation
Client functionality can be seen in `client.py`. Few notable things here are the creation of the connection to the server (line 1), creation of the message (2) and procedure invocation itself (lines 3, 4). 

```
with grpc.insecure_channel('localhost:50051') as channel:
    args = left_pad_pb2.LeftPadInput(string_to_pad=string_to_pad, len=length, ch=ch)
	stub = left_pad_pb2_grpc.LeftPadServiceStub(channel)
    response = stub.left_pad(args) 
```

## Running the example

Running examples in `1-left-pad` directory result in the following.

```
$ python3 server.py
Listening on port 50051
Received string=pad me! from peer ipv6:[::1]:50146
Received string=pad me with zeros!! from peer ipv6:[::1]:50146
```

```
$ python3 client.py
    pad me!
00000pad me with zeros!!
```


## Handling multiple connections and load-balancing With Nginx

Connections to multiple servers can established by creating multiple channel objects and calling remote procedure as described previously.

```
with grpc.insecure_channel('localhost:50051') as channel1,\
             grpc.insecure_channel('localhost:50052') as channel2:
## call remote procedure(s) here as before
```

```
$ python3 server -port 50051
Listening on port 50051
Received string=pad me! from peer ipv6:[::1]:35552
```

TODO describe
```
$ python3 server -port 50052
Listening on port 50052
Received string=pad me with zeros!! from peer ipv6:[::1]:48626
```

TODO describe 

```
$ python3 client.py --multi
    pad me!
00000pad me with zeros!!
```


Copy config file to `/usr/share/nginx` directory, and run `sudo nginx -c <config_file_name>`. To stop running nginx instance, `sudo nginx -s stop`.

In config, nginx server is running on port 505000. Run several instances of `server.py` bound to ports `505001` and `50002` and run `client.py` a couple of times to see round-robin load balancing in action.


# Example 2 - Portable Pixmap streaming

This example demonstrates streaming capabilities of gRPC by the means of the service that allows uploading and downloading images in PPM format as well as modifying them. 


## Interface specification 
gRPC supports four kinds of procedure calls (see `pgm_store.proto`). Note the use of `stream` keyword.

1. Single message in - single message out (as seen in previous example).
2. Single message in - sequence of messages out.

```
rpc get_image(GetImageInput) returns (stream PixelData) { }
```

2. Sequence of messages in - single message out.

```
rpc write_image(stream PixelData) returns (Empty) { }
```

3. Sequence of messages in - sequence of messages out.

```
rpc greyscale(stream PixelData) returns (stream PixelData) { }
```


## Implementation Details 

When calling remote procedure that accepts sequence of messages iterator of said messages is required to be passed. That can be done quite easily by either calling `iter(message_list)` (where `message_list` is `Iterable`) or by using using generators: 

```
def send_pixel_data():
	## ignore first 4 elements
	for i in range(4, len(image_data), 3):
		r = int(image_data[i+0])
		g = int(image_data[i+1])
		b = int(image_data[i+2])
		yield pgm_store_pb2.PixelData(r=r, g=g, b=b)
```

Another topic of interest here is addition of metadata both client and servers can add additional metadata before messages are sent. Metadata is simply a list key-value pairs where both key and value are strings.

```
metadata = (('w', image_data[1]), 
			('h', image_data[2]), 
			('depth', image_data[3]),
			('filename', filename))
```

Client calls the procedure as follows:

```
response = stub.write_image(send_pixel_data(), metadata=metadata)
```

Server can iterate over received metadata through `context` object. Context object can also be used to send metadata to the client:

```
# receive metadata
for key, value in context.invocation_metadata():
	print(key, value)

# send metadata
metadata = (('w', image_data[1]), 
			('h', image_data[2]), 
			('depth', image_data[3]))
context.send_initial_metadata(metadata)
```

See `server.py` and `client.py` for more details!

## Running the example
Launch the server: `python3 server.py`. Client can be run with the following flags:

1. `--send` - send `tux.png`. `server_tux.png` file will be written.
2. `--recv` - receive `server_tux.png`. `client_tux.png` file will be written.
3. `--grey` - stream `tux.png` to server, and write received greyscale image to `greyscale_tux.png`.

## References for this section. 
* https://grpc.io/docs/guides/concepts/



##  Example 3 - key-value-store

This example demonstrates concurrent writes to key-value store which stores simple string-integer pairs as well as error handling. Files of interest are located in `3-key-value-store directory`.


## Concurrent data modification
Concurrent data modification can be handled with either synchronization primitives provided by languages (e.g.  mutexes) or providing `maximum_concurrent_rpcs` argument when instantiating `grpc.server`. It will ensure that only specified number of procedure calls can run concurrently and any new RPC attempts will be discarded without queueing incoming request. `maximum_concurrent_rpcs` should be less or equal to number of worker threads otherwise requests get queued, as expected.

Here's an example execution. Start `server.py` first and then launch clients.

```
$ python3 server.py -sleep 5
Peer ipv6:[::1]:35578 enters critical section with key=x value=15
Peer ipv6:[::1]:35578 exits critical section
```

```
$ python3 client.py  --put -key x -val 15
15 // value we have written!
```

If another client connects before previous procedure call completes, he will receive the following message : 

```
$ python3 client.py  --put -key y -val 44
RpcError caught, code: StatusCode.RESOURCE_EXHAUSTED details: Concurrent RPC limit exceeded!
```

## Exception handling 

In case if remote procedure throws an exception, information about exception gets transmitted to clients. Exceptions can be handled manually by using server's `context` object where status code and details can be explicitly set. 

```
try:
	val = self.store[request.key] 
	ret = kv_store_pb2.Value(value=val)
except KeyError:
	context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
	context.set_details( 'Invalid key {}'.format(request.key) )
	ret = kv_store_pb2.Value()
```

More status codes can be found [here](https://grpc.github.io/grpc/python/grpc.html#channel-connectivity). 

Starting the server `python3 server.py` and launching `python3 client.py --get -key x` will result in the following message delivered to client as expected from code snippet above.

```
RpcError caught, code: StatusCode.INVALID_ARGUMENT details: Invalid key x
```










# Example 4 - add new field to message.

1. Comment out `string_value` in `PutValueInput` and `Value` messages.

todo add error codes




## Todo
* Try out interceptors. 
* A bit more interesting examples. 
* Service failure handling.
* Add more things to the todo list :))
