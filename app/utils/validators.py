import ipaddress
import socket
from urllib.parse import urlparse, urljoin

from fastapi import HTTPException


def validate_public_url(raw_url: str) -> str:
    """Allow only public HTTP(S) destinations to reduce SSRF risk."""
    parsed = urlparse(raw_url)

    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http and https URLs are allowed.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="Please provide a valid public website URL.")
    if parsed.port and parsed.port not in {80, 443}:
        raise HTTPException(status_code=400, detail="Custom ports are not allowed.")

    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise HTTPException(status_code=400, detail="Local and internal addresses are not allowed.")

    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Website domain could not be resolved.")

    if not addresses:
        raise HTTPException(status_code=400, detail="Website domain has no public address.")

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise HTTPException(status_code=400, detail="Private or non-public network addresses are not allowed.")

    return raw_url


def validate_redirect(base_url: str, location: str) -> str:
    return validate_public_url(urljoin(base_url, location))
