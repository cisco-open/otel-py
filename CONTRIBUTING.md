## How to contribute
1. git fork otel-py code
2. if using PyCharm - go to Preferences > Python Interpreter > and use poetry interpreter.
3. run `poetry build`
4. run `make all`
5. to run tests: `make test`
6. to generate .proto files: `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. hello.proto`
