import cisco_telescope

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk import environment_variables
from opentelemetry.semconv.resource import ResourceAttributes
from cisco_telescope import tracing
from pkg_resources import get_distribution

trace_provider = tracing.init(
    cisco_token="eps_nSDuOwGmFpzlXanbr5Fr8oJBIP7QyRC6fOpVxNn94Xw", service_name="shalev", debug=True
)

import requests

requests.get("https://google.com")