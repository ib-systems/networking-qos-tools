import logging
import openstack
from promql import get_top_tap_interfaces

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def find_ports_by_tap_interfaces(interfaces):
    log.info("Connecting to OpenStack cloud='openstack'")
    conn = openstack.connect(cloud="openstack")

    log.info("Fetching all ports from OpenStack")
    ports = {p.id: p for p in conn.network.ports()}
    log.info("Fetched %d ports", len(ports))

    results = []
    matched = 0
    for iface in interfaces:
        tap_prefix = iface["device"].removeprefix("tap")
        matching_port = next((p for pid, p in ports.items() if pid.startswith(tap_prefix)), None)
        if matching_port:
            log.debug("Matched %s -> port %s (%s)", iface["device"], matching_port.id, matching_port.name)
            results.append({**iface, "port_id": matching_port.id, "port_name": matching_port.name})
            matched += 1
        else:
            log.warning("No port found for interface %s (prefix=%s)", iface["device"], tap_prefix)
            results.append({**iface, "port_id": None, "port_name": None})

    log.info("Matched %d/%d interfaces to ports", matched, len(interfaces))
    return results


if __name__ == "__main__":
    log.info("Fetching top tap interfaces from PromQL")
    interfaces = get_top_tap_interfaces()
    log.info("Got %d interfaces from PromQL", len(interfaces))

    results = find_ports_by_tap_interfaces(interfaces)

    print()
    print(f"{'Device':<25} {'TX Avg':>8} {'RX Avg':>8}  {'Port ID':<38} {'Port Name'}")
    print("-" * 120)
    for r in results:
        port_id = r["port_id"] or "NOT FOUND"
        port_name = r["port_name"] or ""
        print(f"{r['device']:<25} {r['tx_avg_mbps']:>8.1f} {r['rx_avg_mbps']:>8.1f}  {port_id:<38} {port_name}")
