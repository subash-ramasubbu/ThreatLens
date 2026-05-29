def generate_tags(threat_type: str, description: str, existing_tags: str) -> str:
    tags = set(t.strip() for t in existing_tags.split(",") if t.strip())
    text = f"{description} {existing_tags}".lower()

    # IP-based tags
    if threat_type == "ip":
        tags.add("malicious-ip")
        if "tor" in text:
            tags.add("tor-exit-node")
        if "scan" in text:
            tags.add("scanning")
        if "brute" in text:
            tags.add("brute-force")
        if "proxy" in text or "vpn" in text:
            tags.add("anonymization")
        if "spam" in text:
            tags.add("spam")
        if "c2" in text or "command" in text or "control" in text:
            tags.add("c2")
        if "botnet" in text:
            tags.add("botnet")
        if "ransomware" in text:
            tags.add("ransomware-c2")

    # Domain-based tags
    elif threat_type == "domain":
        tags.add("malicious-domain")
        if "phish" in text:
            tags.add("phishing")
        if "malware" in text:
            tags.add("malware-distribution")
        if "typosquat" in text:
            tags.add("typosquatting")

    # Hash-based tags
    elif threat_type == "hash":
        tags.add("malicious-file")
        if "ransomware" in text:
            tags.add("ransomware")
        if "trojan" in text:
            tags.add("trojan")
        if "spyware" in text:
            tags.add("spyware")
        if "worm" in text:
            tags.add("worm")

    # CVE-based tags
    elif threat_type == "cve":
        tags.add("vulnerability")
        if "remote code" in text or "rce" in text:
            tags.add("rce")
        if "privilege" in text:
            tags.add("privilege-escalation")
        if "injection" in text:
            tags.add("injection")
        if "overflow" in text:
            tags.add("buffer-overflow")
        if "xss" in text:
            tags.add("xss")
        if "sql" in text:
            tags.add("sql-injection")

    return ",".join(sorted(tags))