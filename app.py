from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
import os
import psycopg2

DB_HOST = "terraform-app-db.c8nk4ikeo0sn.us-east-1.rds.amazonaws.com"
DB_NAME = "cloudcost"
DB_USER = "cloudadmin"


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=os.environ["DB_PASSWORD"],
        sslmode="require"
    )


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        body = json.dumps(data).encode()

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/health":
            self.send_json(200, {
                "status": "healthy",
                "server": socket.gethostname()
            })
            return

        if self.path == "/costs":
            try:
                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT id, service_name, cost, usage_date
                    FROM cloud_costs
                    ORDER BY usage_date, id
                """)

                rows = cursor.fetchall()

                cursor.close()
                connection.close()

                costs = []

                for row in rows:
                    costs.append({
                        "id": row[0],
                        "service_name": row[1],
                        "cost": float(row[2]),
                        "usage_date": str(row[3])
                    })

                self.send_json(200, {
                    "count": len(costs),
                    "cloud_costs": costs
                })

            except Exception as error:
                self.send_json(500, {
                    "error": str(error)
                })

            return

        if self.path == "/":
            self.send_json(200, {
                "message": "Cloud Cost API is running",
                "server": socket.gethostname(),
                "endpoints": [
                    "/health",
                    "/costs"
                ]
            })
            return

        self.send_json(404, {
            "error": "Endpoint not found"
        })

    def log_message(self, format, *args):
        return


server = HTTPServer(("0.0.0.0", 8000), Handler)

print("Cloud Cost API running on port 8000")

server.serve_forever()
