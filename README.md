# Immunoodle Signup

Local development is as below. This application is meant to be run in a container as part of the Immunoodle application stack.

## Setup Environment

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run App Locally

```shell
source venv/bin/activate
python main.py
```

## gRPC Python Setup

```shell
# Download api.proto for a given version.
DEX_VERSION=v2.41.1
wget https://raw.githubusercontent.com/dexidp/dex/${DEX_VERSION}/api/v2/api.proto
mv api.proto dex.proto

# Generate the client bindings.
pip install grpcio-tools
python -m grpc_tools.protoc  -I. --python_out=. --pyi_out=. --grpc_python_out=. dex.proto
```
