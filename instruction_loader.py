import requests

AGNET_DOC_ID = "1TvTT2zpVQtIBYtEaTZ2e2jUXAmKdgDfCW4Slb01jJJo"
AGENT_DOC_URL = f"https://docs.google.com/document/d/{AGNET_DOC_ID}/export?format=txt"

def load_agent_instruction():
    try:
        r = requests.get(AGENT_DOC_URL, headers={"Cache-Control": "no-cache"})
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        print("Failed to load instruction:", e)
        return "You are a helpful assistant."


GREET__DOC_ID = "1QJf_wvw6b7w7VQS55Ib__FjDTfliqDSZSMG3HmbySQI"
GREET_DOC_URL = f"https://docs.google.com/document/d/{GREET__DOC_ID}/export?format=txt"

def load_greet_instruction():
    try:
        r = requests.get(GREET_DOC_URL, headers={"Cache-Control": "no-cache"})
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        print("Failed to load greet instruction:", e)
        return " "
