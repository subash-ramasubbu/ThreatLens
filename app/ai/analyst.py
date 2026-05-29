from groq import Groq
from app.core.config import settings
from app.db.models import ThreatIndicator

client = Groq(api_key=settings.GROQ_API_KEY)


def build_threat_context(threat: ThreatIndicator) -> str:
    return f"""
Threat Indicator Analysis Request:

Type: {threat.type.upper()}
Value: {threat.value}
Severity: {threat.severity.upper()}
Risk Score: {threat.risk_score}/100
Source: {threat.source}
Tags: {threat.tags}
Description: {threat.description}
Country: {threat.country}
First Seen: {threat.first_seen}
Last Seen: {threat.last_seen}
""".strip()


def analyze_threat(threat: ThreatIndicator) -> dict:
    if not settings.GROQ_API_KEY:
        return {"error": "Groq API key not configured"}

    context = build_threat_context(threat)

    prompt = f"""You are an expert SOC analyst and threat intelligence specialist.
Analyze the following threat indicator and provide a detailed security assessment.

{context}

Provide your analysis in exactly this structure:

SUMMARY:
[2-3 sentence plain English summary of what this threat is]

THREAT ASSESSMENT:
[Explain the nature and behavior of this threat]

ATTACK TECHNIQUES:
[List the MITRE ATT&CK techniques this threat is associated with and explain each]

POTENTIAL IMPACT:
[What damage could this threat cause to an organization]

RECOMMENDED ACTIONS:
[Specific steps a security team should take immediately]

CONFIDENCE LEVEL:
[Your confidence in this assessment: HIGH/MEDIUM/LOW and why]
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity analyst specializing in threat intelligence and incident response. Provide precise, actionable security analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.3,
        )

        analysis = response.choices[0].message.content
        sections = parse_analysis(analysis)

        return {
            "threat_id": threat.id,
            "threat_value": threat.value,
            "threat_type": threat.type,
            "risk_score": threat.risk_score,
            "analysis": sections,
            "raw_analysis": analysis,
        }

    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}


def parse_analysis(text: str) -> dict:
    sections = {
        "summary": "",
        "threat_assessment": "",
        "attack_techniques": "",
        "potential_impact": "",
        "recommended_actions": "",
        "confidence_level": "",
    }

    current_section = None
    lines = text.strip().split("\n")

    section_map = {
        "SUMMARY:": "summary",
        "THREAT ASSESSMENT:": "threat_assessment",
        "ATTACK TECHNIQUES:": "attack_techniques",
        "POTENTIAL IMPACT:": "potential_impact",
        "RECOMMENDED ACTIONS:": "recommended_actions",
        "CONFIDENCE LEVEL:": "confidence_level",
    }

    for line in lines:
        line = line.strip()
        matched = False
        for key, section in section_map.items():
            if line.startswith(key):
                current_section = section
                remainder = line[len(key):].strip()
                if remainder:
                    sections[current_section] = remainder
                matched = True
                break
        if not matched and current_section and line:
            if sections[current_section]:
                sections[current_section] += " " + line
            else:
                sections[current_section] = line

    return sections


def analyze_custom_indicator(indicator: str, indicator_type: str) -> dict:
    if not settings.GROQ_API_KEY:
        return {"error": "Groq API key not configured"}

    prompt = f"""You are an expert SOC analyst.
Analyze this {indicator_type.upper()} indicator: {indicator}

Provide analysis in this structure:

SUMMARY:
[What is this indicator]

THREAT ASSESSMENT:
[Is this malicious, suspicious, or benign based on your knowledge]

ATTACK TECHNIQUES:
[Relevant MITRE ATT&CK techniques if applicable]

POTENTIAL IMPACT:
[What could happen if this is malicious]

RECOMMENDED ACTIONS:
[What should a security analyst do]

CONFIDENCE LEVEL:
[HIGH/MEDIUM/LOW and why]
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity analyst. Provide precise threat intelligence analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.3,
        )

        analysis = response.choices[0].message.content
        sections = parse_analysis(analysis)

        return {
            "indicator": indicator,
            "type": indicator_type,
            "analysis": sections,
            "raw_analysis": analysis,
        }

    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}