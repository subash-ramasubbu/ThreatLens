MITRE_MAPPING = {
    # Execution
    "powershell": {"id": "T1059.001", "name": "PowerShell"},
    "script": {"id": "T1059", "name": "Command and Scripting Interpreter"},
    "macro": {"id": "T1059.005", "name": "Visual Basic"},

    # Persistence
    "registry": {"id": "T1547.001", "name": "Registry Run Keys"},
    "startup": {"id": "T1547", "name": "Boot or Logon Autostart Execution"},
    "scheduled": {"id": "T1053", "name": "Scheduled Task/Job"},
    "backdoor": {"id": "T1543", "name": "Create or Modify System Process"},

    # Defense Evasion
    "obfuscat": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "encode": {"id": "T1027", "name": "Obfuscated Files or Information"},
    "rootkit": {"id": "T1014", "name": "Rootkit"},
    "antivirus": {"id": "T1562.001", "name": "Disable or Modify Tools"},

    # Command and Control
    "c2": {"id": "T1071", "name": "Application Layer Protocol"},
    "beacon": {"id": "T1071", "name": "Application Layer Protocol"},
    "tor": {"id": "T1090", "name": "Proxy"},
    "proxy": {"id": "T1090", "name": "Proxy"},
    "botnet": {"id": "T1583", "name": "Acquire Infrastructure"},

    # Impact
    "ransomware": {"id": "T1486", "name": "Data Encrypted for Impact"},
    "encrypt": {"id": "T1486", "name": "Data Encrypted for Impact"},
    "wipe": {"id": "T1485", "name": "Data Destruction"},
    "ddos": {"id": "T1498", "name": "Network Denial of Service"},

    # Credential Access
    "brute": {"id": "T1110", "name": "Brute Force"},
    "credential": {"id": "T1555", "name": "Credentials from Password Stores"},
    "keylog": {"id": "T1056.001", "name": "Keylogging"},
    "phish": {"id": "T1566", "name": "Phishing"},

    # Discovery
    "scan": {"id": "T1046", "name": "Network Service Discovery"},
    "recon": {"id": "T1595", "name": "Active Scanning"},

    # Exfiltration
    "exfil": {"id": "T1041", "name": "Exfiltration Over C2 Channel"},
    "upload": {"id": "T1567", "name": "Exfiltration Over Web Service"},

    # Privilege Escalation
    "privilege": {"id": "T1068", "name": "Exploitation for Privilege Escalation"},
    "rce": {"id": "T1190", "name": "Exploit Public-Facing Application"},
    "overflow": {"id": "T1203", "name": "Exploitation for Client Execution"},
    "injection": {"id": "T1055", "name": "Process Injection"},
}


def map_to_mitre(description: str, tags: str) -> list:
    text = f"{description} {tags}".lower()
    matched = {}

    for keyword, technique in MITRE_MAPPING.items():
        if keyword in text:
            technique_id = technique["id"]
            if technique_id not in matched:
                matched[technique_id] = technique

    return list(matched.values())


def format_mitre_tags(techniques: list) -> str:
    return ",".join(t["id"] for t in techniques)