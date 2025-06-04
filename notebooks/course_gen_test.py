from openai import OpenAI

client = OpenAI()

prompt = """
An aerial view of a single hole of a golf course. 
The hole should be a par 3, with a green, fairway, and sand traps. Delineate the
start and end of the hole with tee boxes and a flagstick. 
"""

response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="hd",
    n=1,
)

print(response.data[0].url)
