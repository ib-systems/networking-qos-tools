import requests
import time
from concurrent.futures import ThreadPoolExecutor

VICTORIA_URL = "http://127.0.0.1:8428"

QUERIES = {
    "tx_avg": 'avg_over_time(rate(node_network_transmit_bytes_total{device=~"^tap.*"}[5m])[2w:5m]) * 8',
    "tx_max": 'max_over_time(rate(node_network_transmit_bytes_total{device=~"^tap.*"}[5m])[2w:5m]) * 8',
    "rx_avg": 'avg_over_time(rate(node_network_receive_bytes_total{device=~"^tap.*"}[5m])[2w:5m]) * 8',
    "rx_max": 'max_over_time(rate(node_network_receive_bytes_total{device=~"^tap.*"}[5m])[2w:5m]) * 8',
}


def _fetch_query(name, query, end):
    response = requests.get(
        f"{VICTORIA_URL}/api/v1/query",
        params={"query": query, "time": end},
    )
    return name, {r["metric"]["device"]: float(r["value"][1]) for r in response.json()["data"]["result"]}


def get_top_tap_interfaces(limit=20):
    end = time.time()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(_fetch_query, name, query, end) for name, query in QUERIES.items()]
        data = {name: result for name, result in (f.result() for f in futures)}

    all_devices = set(data["tx_avg"].keys()) | set(data["rx_avg"].keys())

    results = []
    for device in all_devices:
        results.append({
            "device": device,
            "tx_avg_mbps": round(data["tx_avg"].get(device, 0) / 1e6, 1),
            "tx_max_mbps": round(data["tx_max"].get(device, 0) / 1e6, 1),
            "rx_avg_mbps": round(data["rx_avg"].get(device, 0) / 1e6, 1),
            "rx_max_mbps": round(data["rx_max"].get(device, 0) / 1e6, 1),
        })

    results.sort(key=lambda x: x["tx_avg_mbps"] + x["rx_avg_mbps"], reverse=True)
    return results[:limit]


if __name__ == "__main__":
    import json
    print(json.dumps(get_top_tap_interfaces(), indent=2))
