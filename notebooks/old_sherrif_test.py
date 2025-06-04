from openai import OpenAI

client = OpenAI()

prompt = """
Vector logo design for a run club of an old sherrif surveying the hill country.
"""


response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="hd",
    n=1,
)

print(response.data[0].url)
