import re
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from http import HTTPStatus
from threading import Thread


class BaseHttpTest(unittest.TestCase):
    """
    A base test class for all Http Tests

    The class create an HTTP server for all class test suits
    """

    server, server_thread = None, None

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
                body = "shit"
                self.send_response(HTTPStatus.OK)
                self.send_all_headers(len(body))
                self.end_headers()
                self.wfile.write(bytes(body, 'utf-8'))
            else:
                self.send_error(status)

        def do_POST(self):  # pylint:disable=invalid-name
            status_match = self.STATUS_RE.fullmatch(self.path)
            status = 200
            if status_match:
                status = int(status_match.group(1))
            if status == 200:
                body = "shit"
                self.send_response(HTTPStatus.OK)
                self.send_all_headers(len(body))
                self.wfile.write(bytes(body, 'utf-8'))
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
    def response_headers(cls):
        return {
            "server-response-header": "the response",
            "another-header": "bruh"
        }

    @classmethod
    def run_server(cls):
        httpd = cls.create_server()
        worker = Thread(
            target=httpd.serve_forever, daemon=True, name="Test server worker"
        )
        worker.start()
        return worker, httpd

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server_thread, cls.server = cls.run_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_thread.join()
        super().tearDownClass()
