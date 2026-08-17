"""Load Test & Concurrency Baseline Benchmark Script.

Simulates 10 concurrent workers sending 20 requests each (~200 total)
against the FastAPI decision & market data endpoints to benchmark throughput,
rate limiting protection, and document VPS upgrade trigger conditions.
"""

import sys
import time
import concurrent.futures
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def worker_task(worker_id: int, requests_per_worker: int):
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    ok_200 = 0
    rate_limited_429 = 0
    failures = 0
    latencies = []

    client = TestClient(app)
    for i in range(requests_per_worker):
        sym = symbols[i % len(symbols)]
        start = time.perf_counter()
        try:
            resp = client.get(f"/api/v1/decision/{sym}")
            duration = (time.perf_counter() - start) * 1000.0  # ms
            latencies.append(duration)
            if resp.status_code == 200:
                ok_200 += 1
            elif resp.status_code == 429:
                rate_limited_429 += 1
            else:
                failures += 1
        except Exception:
            failures += 1

    return ok_200, rate_limited_429, failures, latencies


def run_load_benchmark(num_workers: int = 10, reqs_per_worker: int = 20):
    print(f"=== Starting Load Test Baseline: {num_workers} Concurrent Workers x {reqs_per_worker} Reqs ({num_workers * reqs_per_worker} Total) ===")
    
    start_total = time.perf_counter()
    all_latencies = []
    total_200 = 0
    total_429 = 0
    total_failures = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker_task, w, reqs_per_worker) for w in range(num_workers)]
        for f in concurrent.futures.as_completed(futures):
            ok200, rate429, fail, lats = f.result()
            total_200 += ok200
            total_429 += rate429
            total_failures += fail
            all_latencies.extend(lats)

    total_time = time.perf_counter() - start_total
    total_processed = total_200 + total_429 + total_failures
    rps = total_processed / total_time if total_time > 0 else 0
    avg_lat = (sum(all_latencies) / len(all_latencies)) if all_latencies else 0.0
    p95_lat = sorted(all_latencies)[int(len(all_latencies) * 0.95)] if all_latencies else 0.0

    print("=== Load Test Results ===")
    print(f"Total Requests Processed: {total_processed}")
    print(f"Successful Decision Requests (200 OK): {total_200}")
    print(f"Rate-Limiting Throttled Requests (429 Too Many Requests): {total_429}")
    print(f"Unexpected System Failures (5xx): {total_failures}")
    print(f"Total Test Duration: {total_time:.2f} seconds")
    print(f"Throughput Capacity: {rps:.2f} requests/sec")
    print(f"Average Response Latency: {avg_lat:.2f} ms")
    print(f"P95 Response Latency: {p95_lat:.2f} ms")
    print("=========================")

    return {
        "total_requests": total_processed,
        "success_rate_pct": ((total_200 + total_429) / total_processed) * 100.0 if total_processed > 0 else 0,
        "throughput_rps": rps,
        "avg_latency_ms": avg_lat,
        "p95_latency_ms": p95_lat
    }


if __name__ == "__main__":
    run_load_benchmark()
