from bot.external_services.chatgpt4 import OpenaiSession


async def create_image(prompt: str):
    client = OpenaiSession().client
    response = client.images.generate(
      model="dall-e-3",
      style="vivid", #natural
      prompt=f"{prompt}",
      size="1024x1024",
      quality="standard",
      n=1,
    )
    image_url = response.data[0].url
    return image_url