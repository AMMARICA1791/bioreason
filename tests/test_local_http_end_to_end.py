"""Exercise the real HTTP adapter against a local OpenAI-compatible server."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from bioreason.council import run_council, verify_chain

PAPERS = [
    {"title": "Protein folding methods", "id": "1", "source": "SYNTHETIC"},
    {"title": "Protein folding analysis", "id": "2", "source": "SYNTHETIC"},
]


class Handler(BaseHTTPRequestHandler):
    calls = []

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(size))
        self.calls.append(payload)
        body = json.dumps({
            "choices": [{"message": {"content": "Tentative analysis, not validated"}}]
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class LocalModelEndToEndTests(unittest.TestCase):
    def test_real_http_adapter_and_three_roles(self):
        Handler.calls = []
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            import os
            from unittest.mock import patch
            endpoint = "http://127.0.0.1:%d/v1/chat/completions" % server.server_port
            with patch.dict(os.environ, {
                "BIOREASON_MODEL_ENDPOINT": endpoint,
                "BIOREASON_MODEL_NAME": "test-stub",
                "BIOREASON_MODEL_API_KEY": "",
            }):
                output = run_council(
                    "protein folding", PAPERS,
                    model_roles=("Analyst", "Inventor", "Critic"),
                )
            self.assertEqual(len(Handler.calls), 3)
            self.assertTrue(verify_chain(output["messages"]))
            self.assertEqual(output["results"]["Validator"]["verified_findings"], 0)
            for role in ("Analyst", "Inventor", "Critic"):
                self.assertEqual(
                    output["results"][role]["model_suggestion"]["status"],
                    "unverified model-generated suggestion",
                )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
