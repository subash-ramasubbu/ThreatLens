from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_threat_report(threats_summary: dict) -> dict:
    if not settings.GROQ_API_KEY:
        return {"error": "Groq API key not configured"}

    prompt = f"""You are a senior threat intelligence analyst.
Based on the following threat data summary, write a professional threat intelligence report.

Data Summary:
- Total threats: {threats_summary.get('total', 0)}
- Critical threats: {threats_summary.get('critical', 0)}
- High threats: {threats_summary.get('high', 0)}
- Medium threats: {threats_summary.get('medium', 0)}
- Top sources: {threats_summary.get('sources', [])}
- Top tags: {threats_summary.get('tags', [])}
- Sample threats: {threats_summary.get('samples', [])}

Write a professional report with:
1. Executive Summary
2. Key Findings
3. Top Threats
4. Attack Pattern Analysis
5. Recommendations
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior threat intelligence analyst writing professional security reports."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1200,
            temperature=0.4,
        )

        return {
            "report": response.choices[0].message.content,
            "threats_analyzed": threats_summary.get('total', 0),
        }

    except Exception as e:
        return {"error": f"Report generation failed: {str(e)}"}