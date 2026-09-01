import random
from pathlib import Path

def generate_log_file(filename: str = "server.log", num_lines: int = 5_000_000) -> None:
    print(f"Generating {filename} with {num_lines} lines...")
    endpoints = ["/api/v1/users", "/api/v1/orders", "/health", "/login", "/logout"]
    status_codes = [200, 201, 400, 401, 404, 500]
    
    path = Path(filename)
    with path.open("w", encoding="utf-8") as f:
        for _ in range(num_lines):
            endpoint = random.choice(endpoints)
            status = random.choice(status_codes)
            f.write(f"2026-09-01 12:00:00 [INFO] GET {endpoint} - Status: {status}\n")
    print("Log file generated successfully.")

if __name__ == "__main__":
    generate_log_file()