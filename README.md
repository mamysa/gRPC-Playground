# gRPC Playground

Compile proto as follows:

`python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. filename.proto`

Run `python3 client.py` and `python3 server.py`.


## Load Balancing With Nginx
Copy config file to `/usr/share/nginx` directory, and run `sudo nginx -c <config_file_name>`. To stop running nginx instance, `sudo nginx -s stop`.

In config, nginx server is running on port 505000. Run several instances of `server.py` bound to ports `505001` and `50002` and run `client.py` a couple of times to see round-robin load balancing in action.


## Todo
* Try out interceptors. 
* A bit more interesting examples. 
* Service failure handling.
* Add more things to the todo list :))
