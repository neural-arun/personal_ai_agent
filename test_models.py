import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("d:/agentic_projects/personal_career_agent/.env")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "save_user_details",
            "description": "Save contact details when user shows interest.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
            },
        },
    }
]

try:
    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=[{"role": "user", "content": "hi"}],
        tools=tools,
        tool_choice="auto",
    )
    print("SUCCESS")
    print(response.choices[0].message)
except Exception as e:
    print("ERROR:", str(e))
