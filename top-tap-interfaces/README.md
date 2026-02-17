# top-tap-interfaces

Identify the highest bandwidth tap interfaces using PromQL metrics from VictoriaMetrics, match them to OpenStack ports, and apply QoS policies.

## Modules

### promql.py

Queries VictoriaMetrics for tap interface traffic stats over a 2-week window.

```python
from promql import get_top_tap_interfaces

results = get_top_tap_interfaces(limit=20)
# [{"device": "tape0701dea-03", "tx_avg_mbps": 337.5, "tx_max_mbps": 382.5, "rx_avg_mbps": 317.6, "rx_max_mbps": 359.7}, ...]
```

Returns an ordered list of dicts sorted by combined TX+RX average throughput (descending). Metrics are in Mbps.

Configure `VICTORIA_URL` in the file (default: `http://127.0.0.1:8428`).

### openstack-port-set-qos-policy.py

Sets a QoS policy on an OpenStack port.

```python
from openstack_port_set_qos_policy import set_qos

set_qos("port-uuid", "my-qos-policy")
```

### main.py

Ties it all together: fetches top tap interfaces, resolves them to OpenStack ports by matching the tap name prefix (`tap<uuid-prefix>`) to port UUIDs, and prints a summary table.

```
python3 main.py
```

Example output:

```
2025-01-01 12:00:00 INFO Fetching top tap interfaces from PromQL
2025-01-01 12:00:01 INFO Got 20 interfaces from PromQL
2025-01-01 12:00:01 INFO Connecting to OpenStack cloud='openstack'
2025-01-01 12:00:02 INFO Fetching all ports from OpenStack
2025-01-01 12:00:03 INFO Fetched 150 ports
2025-01-01 12:00:03 INFO Matched 19/20 interfaces to ports

Device                    TX Avg   RX Avg  Port ID                                Port Name
------------------------------------------------------------------------------------------------------------------------
tape0701dea-03             337.5    317.6  e0701dea-0312-4a5b-8c1a-...             my-vm-port
```

## Requirements

- Python 3.9+
- `requests`
- `openstacksdk`

OpenStack credentials via `clouds.yaml` or environment variables.
