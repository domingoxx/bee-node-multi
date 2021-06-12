#!/bin/bash
export BEE_API_SECURE_KEY="123"
export BEE_VERSION="0.6.2"
export BEE_CONFIG_PATH_INDEX="1"
export BEE_MACHINE_NAME="XCW-1"
export BEE_MACHINE_GROUP="LOCAL"
export BEE_STORE_PATH="."
export BEE_ADMIN_BASE_API="http://127.0.0.1:8080/jeecg-bee"


python3.8 -m py.start.py