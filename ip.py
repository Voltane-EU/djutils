import ipaddress

def mask_ip_address(ip_address):
    """
    Mask a IP-Address so that it is GDPR conform.
    For IPv4 Addresses the last 8 bits are dropped.
    For IPv6 Addresses the last 72 bits are dropped.
    """
    ip_address = ipaddress.ip_network(ip_address)
    return str(ip_address.supernet(prefixlen_diff=8 if isinstance(ip_address, ipaddress.IPv4Network) else 72).network_address)
