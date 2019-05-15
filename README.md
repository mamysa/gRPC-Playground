# gRPC Playground
gRPC is a remote procedure call framework developed by Google. It uses protobuf (protocol buffers) as interface definition language (by default) and uses HTTP/2 protocol for exchanging messages (i.e. binary protocol and allows for multiplexing (multiple requests can be served through single TCP connection). gRPC supports many different programming languages such as Java, C++ and Python.

1. Specify data types and services using specification language.
2. Compile specification into language of choice.  
3. Implement functionality behind the interface. 
4. Call desired procedure. 

The demo consists of four parts.

* Example 1 - Left Pad shows an example of simple RPC.
* Example 2 - Portable Pixmap streaming demonstrates streaming capabilities of gRPC.
* Example 3 and Example 4 - Key-Value store demonstrate synchronization and interface compatibility.

# Installation 
For the demo Python will be used. gRPC can be installed using `pip`.

```
$ python -m pip install grpcio
$ python -m pip install grpcio-tools
```

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

In the example below the client makes two procedure calls that connect to different servers. 

```
$ python3 server -port 50051
Listening on port 50051
Received string=pad me! from peer ipv6:[::1]:35552
```

```
$ python3 server -port 50052
Listening on port 50052
Received string=pad me with zeros!! from peer ipv6:[::1]:48626
```

```
$ python3 client.py --multi
    pad me!
00000pad me with zeros!!
```

There's no need for client to connect to two servers that provide the same functionality (and expose their IP addresses!). It is possible to use nginx to route requests to different servers and perform load-balancing. Configuration for nginx looks like this: 

```
events { }
http {
	upstream leftpad_app {
		server 127.0.0.1:50051;
		server 127.0.0.1:50052;
	}

	server {
		listen 50050 http2;
		location / {
			grpc_pass grpc://leftpad_app;
		}
	}
}
```

First, two instances of gRPC server are specified in `leftpad_app` group. All requests arriving to the server are proxied to servers specified `leftpad_app`. By default, round-robin scheduling is used.

To run the example, you may need to copy provided configuration file to `/usr/share/nginx` directory, and run `sudo nginx -c nginx-load-balance.conf`. 

Start couple of servers and bind them to ports `50051` and `50052` and then run the client. As client calls the remote procedure twice, both servers will used. Here's expected output: 

```
$ python3 server.py --port 50051
Listening on port 50051
Received string=pad me! from peer ipv4:127.0.0.1:54376
```

```
$ python3 server.py --port 50052
Listening on port 50051
Received string=pad me! from peer ipv4:127.0.0.1:54376
```

```
$ python client.py --port 50050
    pad me!
00000pad me with zeros!!
```

To stop running nginx instance, use `sudo nginx -s stop`.


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



# Example 3 - key-value-store

This example demonstrates concurrent writes to key-value store which stores simple string-integer pairs as well as error handling. Files of interest are located in `3-key-value-store` directory.

A client can call `put_value` and `get_value` procedures. `put_value` expects a message containing a `string` and `int64` and returns most recently stored value (i.e. also an `int64`). `get_value` expects a message containing a `string` and also returns `int64`. Full specification can be found in `kv_store.proto` file.

```
syntax = "proto3";

service KeyValueStoreService {
	rpc put_value(PutValueInput) returns (Value) { }
	rpc get_value(GetValueInput) returns (Value) { }
}

message GetValueInput {
	string key = 1;
}

message PutValueInput {
	string key = 1;
	int64 value = 2;
}

message Value {
	int64 value = 1;
}
```

## Concurrent data modification
Concurrent data modification can be handled with either synchronization primitives provided by languages (e.g.  mutexes) or providing `maximum_concurrent_rpcs` argument when instantiating `grpc.server`. 

```
server = grpc.server(futures.ThreadPoolExecutor(max_workers=1), maximum_concurrent_rpcs=1)
```

It will ensure that only specified number of procedure calls can run concurrently and any new RPC attempts will be discarded without queueing incoming request. `maximum_concurrent_rpcs` should be less or equal to number of worker threads otherwise requests get queued, as expected.

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

If another client happens to call a procedure before previous procedure call completes, he will receive the following message : 

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



# Example 4 - key-value store v2.

Revelant files to this example are located in `3-key-value-store` and `4-key-value-store-v2`.

This particular example modifies functionality provided by key-value store seen in Example 3 and demonstrates backward and forward compatibility. Instead of taking a single integer as an input, new version of key-value store may take a pair of integers and perform computation involving those (add or multiply) prior to storing the final value. 

proto3 specification for `4-key-value-store-v2` example is listed below. Only two changes from specification of `3-key-value-store` are 1. the addition of another `int64` field and 2. addition of operator to act on inputs.

If `ASSIGN` operator is provided then only `val1` is stored in the key-value store.

```
enum Operator {
		ASSIGN = 0;
		ADD = 1;
		MUL = 2;
}

service KeyValueStoreService {
	rpc put_value(PutValueInput) returns (Value) { }
	rpc get_value(GetValueInput) returns (Value) { }
}

message GetValueInput {
	string key = 1;
}

message PutValueInput {
	string key = 1;
	int64 val1 = 2;
	// Adding new fields is allowed.
	int64 val2 = 3;
	Operator op = 4; 
}

message Value {
	int64 value = 1;
}
```

Such addition doesn't break compatibility. 

* **Backward compatibility** (V1 client - V2 server) -client is not aware of new fields and server will replace missing fields with default values.
* **Forward compatibility** (V2 client - V1 server) - since binary message is still well-formed, unknown fields can be ignored.



## Running examples

Backward compatibility.
```
$ python3 4-key-value-store-v2/server.py
Running KVStoreV2
Peer ipv6:[::1]:35714 enters critical section with key=x val1=12 val2=0 op=0
Peer ipv6:[::1]:35714 exits critical section
```

```
$ python3 3-key-value-store/client.py --get -key x 
12
$ python3 3-key-value-store/client.py --put -key x -val 12
12
```

Forward compatibility:

```
$ python3 3-key-value-store/server.py
Peer ipv6:[::1]:35734 enters critical section with key=x value=5
Peer ipv6:[::1]:35734 exits critical section
! we don't print anything for get_key
```

```
$ python3 4-key-value-store-v2/client.py --put -val1 5 -val2 8 -key x --add
5 
python3 4-key-value-store-v2/client.py --get -key x
5
```

# References
Grpc introduction.
* https://grpc.io/docs/guides/concepts/

Grpc installation.
* https://grpc.io/blog/installation/
* https://grpc.io/docs/quickstart/python/

Protocol buffers service specification and default values.
https://developers.google.com/protocol-buffers/docs/proto3#services
https://developers.google.com/protocol-buffers/docs/proto3#default

Protocol buffers message updating and compatibility.
* https://developers.google.com/protocol-buffers/docs/proto3#updating
* https://developers.google.com/protocol-buffers/docs/proto3#unknowns

gRPC Python Reference
* https://grpc.github.io/grpc/python/
