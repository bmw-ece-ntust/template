from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


class _Handler(BaseHTTPRequestHandler):
	def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler naming)
		if self.path not in ("/", "/health"):
			self.send_response(404)
			self.send_header("Content-Type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps({"status": "NOT_FOUND"}).encode("utf-8"))
			return

		self.send_response(200)
		self.send_header("Content-Type", "application/json")
		self.end_headers()

		payload = {
			"status": "OK",
			"service": os.getenv("SERVICE_NAME", "template-app"),
			"timestamp": int(time.time()),
		}
		self.wfile.write(json.dumps(payload).encode("utf-8"))

	def log_message(self, fmt: str, *args: object) -> None:
		# Keep logs concise for container usage.
		print(f"[http] {self.address_string()} - {fmt % args}")


def main() -> None:
	host = os.getenv("HOST", "0.0.0.0")
	port = int(os.getenv("PORT", "8080"))

	server = HTTPServer((host, port), _Handler)
	print(f"Serving on http://{host}:{port} (health: /health)")
	server.serve_forever()


if __name__ == "__main__":
	main()