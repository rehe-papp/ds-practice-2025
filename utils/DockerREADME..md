
# To build the Utils image:

docker build -t ds-practice-2025-utils .

# To generate the proto py files:
cd utils

docker run --rm -v .\:/app ds-practice-2025-utils sh -c "python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./fraud_detection.proto"