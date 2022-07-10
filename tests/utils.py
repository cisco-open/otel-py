"""
Copyright The Cisco Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from os import environ

# SDK test utils
LOCAL_COLLECTOR = "localhost:4317"
TEST_TOKEN = "test_token"
TEST_SERVICE_NAME = "test_service_name"
COLLECTOR_ENDPOINT = "www.mock-random-endpoint.com"
CUSTOM_HEADER_KEY = "custom-header-key"
CUSTOM_HEADER_VALUE = "custom-header-value"


def clean_env_vars(env_var_names):
    for key in env_var_names:
        environ.pop(key, None)


# Instrumentation test utils
MONGODB_SUCCESS_RESPONSE = "'ok': 1.0"
MONGODB_RECORD = {"name": "John", "address": "Highway 37"}
MONGODB_RECORD_STRIPPED = "'name': 'John', 'address': 'Highway 37"
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
