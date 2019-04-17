# gRPC Playground

Compile proto as follows:

`python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. filename.proto`

Run `python3 client.py` and `python3 server.py`.

## Todo
* Try out interceptors. 
* A bit more interesting examples. 
* Service failure handling.
* Add more things to the todo list :))
