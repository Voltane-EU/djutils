import ipaddress

def mask_ip_address(ip_address):
    """
    Mask a IP-Address so that it is GDPR conform.
    For IPv4 Addresses the last 8 bits are dropped.
    For IPv6 Addresses the last 72 bits are dropped.
    (Stripping 72 instead of just 64 bits because most ISPs provide a /64 subnet to each customer so by just removing
    the last 64 bits only the device part is removed, but the ip could still be assigned to a person.)
    """
    ip_address = ipaddress.ip_network(ip_address)
    return str(ip_address.supernet(prefixlen_diff=8 if isinstance(ip_address, ipaddress.IPv4Network) else 72).network_address)
