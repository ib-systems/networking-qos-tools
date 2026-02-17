import openstack


def set_qos(port_id, qos_policy_name):
    conn = openstack.connect()
    policy = conn.network.find_qos_policy(qos_policy_name)
    if policy is None:
        raise ValueError(f"QoS policy '{qos_policy_name}' not found")
    conn.network.update_port(port_id, qos_policy_id=policy.id)
