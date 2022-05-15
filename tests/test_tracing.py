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

import os
import unittest

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk import environment_variables
from opentelemetry.semconv.resource import ResourceAttributes
from cisco_telescope import tracing
from pkg_resources import get_distribution


class TestTracing(unittest.TestCase):
    def test_init_defaults(self):
        trace_provider = tracing.init(
            cisco_token="sometoken", service_name="service", debug=True
        )

        resource = trace_provider.resource

        self.assertIsInstance(resource, Resource)
        self.assertEqual(
            resource.attributes[ResourceAttributes.SERVICE_NAME], "service"
        )
        # sdk_version = get_distribution("cisco_telescope").version
        # self.assertEqual(resource.attributes["cisco.sdk.version"], sdk_version)

    def test_default_open_tel_variables(self):
        default_service_name = "default_service_name"
        os.environ[environment_variables.OTEL_SERVICE_NAME] = default_service_name

        trace_provider = tracing.init(cisco_token="sometoken", debug=True)

        resource = trace_provider.resource
        self.assertEqual(
            resource.attributes[ResourceAttributes.SERVICE_NAME], default_service_name
        )

    def test_configuration_open_tel_variables(self):
        configuration_service_name = "service_name"
        default_service_name = "default_service_name"
        os.environ[environment_variables.OTEL_SERVICE_NAME] = default_service_name

        trace_provider = tracing.init(
            cisco_token="sometoken", service_name=configuration_service_name, debug=True
        )

        resource = trace_provider.resource
        self.assertEqual(
            resource.attributes[ResourceAttributes.SERVICE_NAME],
            configuration_service_name,
        )
