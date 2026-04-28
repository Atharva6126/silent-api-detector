from fastapi import FastAPI, Request
import time

app = FastAPI(title="Silent API Failure Detector")
metrics = []

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    latency = (time.time() - start_time) * 1000

    metric = {
        "endpoint": request.url.path,
        "method": request.method,
        "status": response.status_code,
        "latency_ms": round(latency, 2)
    }

    metrics.append(metric)
    print(metric)

    return response


@app.get("/")
def root():
    return {"message": "Running"}


@app.get("/api/normal")
def normal_api():
    return {"status": "ok", "data": [1, 2, 3]}

@app.get("/api/slow")
def slow_api():
    import time
    time.sleep(2)
    return {"status": "slow response"}

@app.get("/metrics")
def get_metrics():
    return metrics

@app.get("/alerts")
def get_alerts():
    alerts = []

    for metric in metrics:
        if metric["latency_ms"] > 1000:
            alerts.append({
                "endpoint": metric["endpoint"],
                "type": "LATENCY_SPIKE",
                "message": "API response is too slow",
                "latency_ms": metric["latency_ms"],
                "severity": "high"
            })

    return alerts