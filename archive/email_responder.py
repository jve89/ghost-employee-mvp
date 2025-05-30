import openai

def generate_gpt_reply(email_body, openai_api_key):
    openai.api_key = openai_api_key

    prompt = f"""
You are a polite and professional operations coordinator.
Your job is to reply to emails in a clear, concise, and business-like manner.
Use the following rules:
- Start with a friendly but professional opening.
- Summarize the sender's main point.
- Confirm receipt or next steps.
- Use a polite closing line.

Here is the email you received:

{email_body}

Draft a professional reply below:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful and polite office assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5,
        )
        reply_text = response['choices'][0]['message']['content']
        return reply_text.strip()
    except Exception as e:
        print(f"[ERROR] GPT generation failed: {e}")
        return "[ERROR] Failed to generate reply."
