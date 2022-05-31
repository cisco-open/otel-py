from cisco_telescope import tracing
from cisco_telescope import options

import requests

opt = options.Options(
    cisco_token="eps_nSDuOwGmFpzlXanbr5Fr8oJBIP7QyRC6fOpVxNn94Xw",
    service_name="shalev",
    debug=True,
    payloads_enabled=True,
    instrumentations=["aiopg", "flask", "sqlite3"]
)
trace_provider = tracing.create_trace_provider(opt)

requests.get("https://www.google.com")
