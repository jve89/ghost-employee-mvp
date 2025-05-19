from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_tasks(summary_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a helpful assistant that extracts clear, actionable tasks from a text. "
                        "Return them as a list. Each task must be on its own line and begin with a dash (-)."
                    )
                },
                {
                    "role": "user",
                    "content": f"Extract all the individual tasks from this summary:\n\n{summary_text}"
                }
            ],
            max_tokens=300,
            temperature=0.2,
        )

        # Split and clean
        lines = response.choices[0].message.content.strip().split("\n")
        tasks = [line.strip("-• ").strip() for line in lines if line.strip()]
        return tasks

    except Exception as e:
        print(f"[ERROR] Failed to extract tasks: {e}")
        return []
