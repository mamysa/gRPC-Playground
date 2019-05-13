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
Received string=pad me! from peer ipv6:[::1]:50146
Received string=pad me with zeros!! from peer ipv6:[::1]:50146
```

```
$ python3 client.py
    pad me!
00000pad me with zeros!!
```







# Example 2 - 2-ppm streaming

# Example 3 - key value store 
Demonstrate synchronization. Nothing too particularly exciting - use usual synchronization primitives provided by the language (e.g. mutexes). Argument of interest for `grpc.server` - `maximum_concurrent_rpcs`. Should be `<=` than number of threads, otherwise requests get queued.

## Load Balancing With Nginx
Copy config file to `/usr/share/nginx` directory, and run `sudo nginx -c <config_file_name>`. To stop running nginx instance, `sudo nginx -s stop`.

In config, nginx server is running on port 505000. Run several instances of `server.py` bound to ports `505001` and `50002` and run `client.py` a couple of times to see round-robin load balancing in action.




# Example 4 - add new field to message.

1. Comment out `string_value` in `PutValueInput` and `Value` messages.

todo add error codes




## Todo
* Try out interceptors. 
* A bit more interesting examples. 
* Service failure handling.
* Add more things to the todo list :))
