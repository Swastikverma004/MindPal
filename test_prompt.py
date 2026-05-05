import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_system_prompt(character: str) -> str:
    meta_prompt = f"""You are a prompt engineer. Generate a detailed system prompt for an AI chatbot that will role-play as: "{character}"

The system prompt should:
1. Define the persona clearly (personality, speech style, tone, mannerisms)
2. If it's a Bollywood character, capture their iconic traits, dialogue style, and emotional patterns
3. If it's a relationship role (therapist, friend, wife, coach), define the relationship dynamic and how they should respond
4. Include instructions to be emotionally supportive, engaging, and stay in character
5. Add quirks, catchphrases, or signature behaviors where relevant
6. Keep responses conversational and human-like
7. Remember previous context in the conversation
8. Speak in a mix of Hindi and English (Hinglish) if it's a Bollywood character or Indian relationship role

Return ONLY the system prompt text, nothing else. Make it rich and detailed (200-300 words)."""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": meta_prompt}],
        max_tokens=500,
        temperature=0.8,
    )
    return resp.choices[0].message.content.strip()

print("Prompt for Wife:")
print(generate_system_prompt("Wife"))
print("-" * 50)
print("Prompt for Life Coach:")
print(generate_system_prompt("Life Coach"))
