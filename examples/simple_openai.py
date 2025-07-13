import json

import weave
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Setup
weave_client = weave.init("quantified-self-test")


@weave.op()
def extract_fruit(sentence: str) -> dict:
    client = OpenAI()
    system_prompt = (
        "Parse sentences into a JSON dict with keys: fruit, color and flavor."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sentence},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    extracted = response.choices[0].message.content
    return json.loads(extracted)


# Test it
sentence = "There are many fruits that were found on the recently discovered planet Goocrux. There are neoskizzles that grow there, which are purple and taste like candy."
result = extract_fruit(sentence)
print(result)
