import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def ask_ai(question):
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="You are a helpful SQL assistant.",
        input=question
    )
    return response.output_text

if __name__ == "__main__":
    answer = ask_ai("What is SQL? Explain in one sentence.")
    print(answer)