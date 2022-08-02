import re
import time
import typing
import unittest
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from opentelemetry.sdk.trace import Span


def test_sanity():
    assert 1 == 1


class BaseHttpTest(unittest.TestCase):
    """A base test class for all Http Tests.

    The class create an HTTP server for all class test suits
    """

    server, server_thread = None, None

    @classmethod
    def request_headers(cls) -> typing.Dict[str, str]:
        return {"test-header-key": "test-header-value"}

    @classmethod
    def response_headers(cls):
        return {"server-response-header": "the response", "another-header": "bruh"}

    @classmethod
    def request_body(cls) -> str:
        return "The request body"

    @classmethod
    def response_body(cls):
        return "The response body"

    def assert_captured_headers(self, span: Span, prefix: str, headers: dict):
        for key, val in headers.items():
            self.assertEqual(span.attributes[f"{prefix}.{key}"], val)

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"  # Support keep-alive.
        # timeout = 3 # No timeout -- if shutdown hangs, make sure to close your connection

        STATUS_RE = re.compile(r"/status/(\d+)")

        def do_GET(self):  # pylint:disable=invalid-name
            status_match = self.STATUS_RE.fullmatch(self.path)
            status = 200
            if status_match:
                status = int(status_match.group(1))
            if status == 200:
                body = BaseHttpTest.response_body()
                self.send_response(HTTPStatus.OK)
                self.send_all_headers(len(body))
                self.end_headers()
                self.wfile.write(bytes(body, "utf-8"))
            else:
                self.send_error(status)

        def do_POST(self):  # pylint:disable=invalid-name
            status_match = self.STATUS_RE.fullmatch(self.path)
            status = 200
            if status_match:
                status = int(status_match.group(1))
            if status == 200:
                body = BaseHttpTest.response_body()
                self.send_response(HTTPStatus.OK)
                self.send_all_headers(len(body))
                self.end_headers()
                self.wfile.write(bytes(body, "utf-8"))
            else:
                self.send_error(status)

        def send_all_headers(self, body_len):
            self.send_header("Content-Length", str(body_len))

            for key, value in BaseHttpTest.response_headers().items():
                self.send_header(key, value)

    @classmethod
    def create_server(cls):
        server_address = ("127.0.0.1", 0)  # Only bind to localhost.
        return HTTPServer(server_address, cls.Handler)

    @classmethod
    def run_server(cls):
        httpd = cls.create_server()
        worker = Thread(
            target=httpd.serve_forever, daemon=True, name="Test server worker"
        )
        worker.start()
        time.sleep(1)

        return worker, httpd

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server_thread, cls.server = cls.run_server()
        http_host = ":".join(map(str, cls.server.server_address[:2]))
        http_url_base = f"http://{http_host}"

        cls.http_url_sanity = f"{http_url_base}/status/200"
        cls.http_url_error = f"{http_url_base}/status/404"

        time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_thread.join()
        super().tearDownClass()
