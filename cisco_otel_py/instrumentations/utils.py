from opentelemetry.trace.span import Span


def lowercase_items(items: dict):  # pylint:disable=R0201
    return {k.lower(): v for k, v in items.items()}


def add_attributes_to_span(prefix: str, span: Span, attributes: dict):
    """set attributes to span"""
    for attribute_key, attribute_value in attributes.items():
        span.set_attribute(f"{prefix}{attribute_key}", attribute_value)
