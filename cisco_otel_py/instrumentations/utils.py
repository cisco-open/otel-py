from opentelemetry.trace.span import Span


def lowercase_items(items: dict):
    return {k.lower(): v for k, v in items.items()}


def add_attributes_to_span(prefix: str, span: Span, attributes: dict):
    """set attributes to span"""
    for attribute_key, attribute_value in attributes.items():
        span.set_attribute(f"{prefix}.{attribute_key}", attribute_value)


# Check body size
def check_body_size(body: str, max_payload_size: int) -> bool:
    if body in (None, ""):
        return False
    body_len = len(body)
    if max_payload_size and body_len > max_payload_size:
        print(f"Truncating body to {max_payload_size} length")
        return True
    return False


def grab_first_n_bytes(body: str, max_payload_size: int) -> str:
    if body in (None, ""):
        return ""
    if check_body_size(body, max_payload_size):
        return body[0, max_payload_size]
    else:
        return body
