# gRPC Playground
gRPC is a remote procedure call framework developed by Google. It uses protobuf (protocol buffers) as interface definition language (by default) and uses HTTP/2 protocol for exchanging messages (i.e. binary protocol and allows for multiplexing (multiple requests can be served through single TCP connection). gRPC supports many different programming languages such as Java/C++/Python, etc.

1. Specify data types and services using specification language.
2. Compile specification into language of choice.  
3. Implement functionality behind the interface. 
4. Call desired interface. 
5. ???
6. Profit!

# Compiling proto  
Compile proto as follows:

`python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. filename.proto`

# Example 1 - Left Pad 
## 

## Load Balancing With Nginx
Copy config file to `/usr/share/nginx` directory, and run `sudo nginx -c <config_file_name>`. To stop running nginx instance, `sudo nginx -s stop`.

In config, nginx server is running on port 505000. Run several instances of `server.py` bound to ports `505001` and `50002` and run `client.py` a couple of times to see round-robin load balancing in action.


# Example 2 - 2-ppm streaming

# Example 3 - key value store 
Demonstrate synchronization. Nothing too particularly exciting - use usual synchronization primitives provided by the language (e.g. mutexes). Argument of interest for `grpc.server` - `maximum_concurrent_rpcs`. Should be `<=` than number of threads, otherwise requests get queued.


# Example 4 - add new field to message.

1. Comment out `string_value` in `PutValueInput` and `Value` messages.

todo add error codes




## Todo
* Try out interceptors. 
* A bit more interesting examples. 
* Service failure handling.
* Add more things to the todo list :))
