import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv() # This reads the .env file

# Try to load from environment or .env file
# For this hackathon, we'll expect the key to be set in the environment or passed directly if hardcoded for testing.
API_KEY = os.environ.get("GEMINI_API_KEY")
# Initialize the new Google GenAI client
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

def diagnose_router(router_detail, question):
    """
    Calls the Gemini API to diagnose a router based on its data.
    """
    if not API_KEY:
        return {
            "cause": "API Key Missing",
            "evidence": ["The GEMINI_API_KEY environment variable is not set."],
            "recommended_fix": "Configure the API key in the backend environment."
        }
        
    # Format the router data into a clean string for the prompt context
    context = f"""
ROUTER CONTEXT:
ID: {router_detail.get('router_id')}
Model: {router_detail.get('model')}
Firmware: {router_detail.get('firmware_version')}
Location: {router_detail.get('building')} - Room {router_detail.get('room')}
User Type: {router_detail.get('user_type')}

HEALTH SCORE: {router_detail.get('health_score')}/100
- Speed Score: {router_detail.get('speed_score')}
- Latency Score: {router_detail.get('latency_score')}
- Packet Loss Score: {router_detail.get('loss_score')}
- Disconnects Score: {router_detail.get('disconnects_score')}
- Signal Score: {router_detail.get('signal_score')}

HOURLY METRICS (24 hours):
"""
    # Add a summary of metrics to keep context window reasonable but informative
    metrics = router_detail.get('metrics', [])
    for m in metrics:
        context += f"Hour {m['hour'][-5:]}: Speed={m['avg_speed_mbps']}Mbps, Lat={m['latency_ms']}ms, Loss={m['packet_loss_pct']}%, Disc={m['disconnects']}, Devs={m['connected_devices']}, Sig={m['signal_dbm']}dBm\n"

    context += "\nCOMPLAINTS:\n"
    complaints = router_detail.get('complaints', [])
    if not complaints:
        context += "No complaints recorded.\n"
    else:
        for c in complaints:
            context += f"- {c['date']}: {c['complaint_text']}\n"

    system_prompt = """
You are a network diagnostics expert analyzing campus Wi-Fi router data.
Based ONLY on the ROUTER CONTEXT provided, answer the user's question.

RULES:
1. Provide the ROOT CAUSE of the issue in one clear sentence.
2. Provide specific EVIDENCE by citing actual numbers from the context (e.g., "At 18:00, connected devices spiked to 35 while speed dropped to 2Mbps"). NEVER invent or guess data.
3. Recommend EXACTLY ONE fix from this list: "firmware_update", "relocate", "replace", "user_education".
   - If signal is constantly worse than -70 dBm, recommend "relocate".
   - If the router is overloaded with devices in the evening, recommend "user_education".
   - If old firmware (not latest) is paired with frequent disconnects, recommend "firmware_update".
   - If metrics are generally healthy but users complain, recommend "user_education".
   - If hardware seems completely faulty (speed < 10Mbps constantly, high loss), recommend "replace".

Output strictly valid JSON with the following schema:
{
  "cause": "string",
  "evidence": ["string1", "string2"],
  "recommended_fix": "string"
}
"""

    prompt = f"{system_prompt}\n\n{context}\n\nUSER QUESTION: {question}"

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        # Parse the JSON response
        result = json.loads(response.text)
        return result
    except Exception as e:
        return {
            "cause": "Error generating diagnosis",
            "evidence": [str(e)],
            "recommended_fix": "Check API logs or data format."
        }
