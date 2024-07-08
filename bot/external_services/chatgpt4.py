import asyncio
import os
import datetime
import requests
from openai import OpenAI
from bot.config_data.config import load_config
config = load_config()


class OpenaiSession:
    def __init__(self, assistant_id=config.open_ai.assistant_id):
        self.client = OpenAI(
            organization=config.open_ai.organization_id,
            api_key=config.open_ai.api_key
        )
        self.assistant = assistant_id
        self.thread = self.client.beta.threads.create()
        #print(f"Создание объекта: {self}")

    async def add_message_to_thread(self, content):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )

    async def run_assistant(self):
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant
        )
        #print(f"Run ассистент: {self.run}")

    async def wait_run_assistant(self):
        status = self.run.status  # начальный статус
        while status != 'completed':
            # Ожидание 3 секунды перед следующей попыткой
            await asyncio.sleep(3)
            status = await self.retrieve_run()
        #time_of_response = self.start_time - self.run.completed_at
        return status

    async def retrieve_run(self):
        run_info = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        #print(run_info)
        return run_info.status

    async def response_gpt(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread.id).data[0].content[0].text.value

    async def clear_context(self):
        self.client.beta.threads.delete(self.thread.id)

    async def recognise_audio_and_voice(self, file_path, file_ext) -> str:  # bot: Bot
        # print(f"Подключились к клиенту: {client}")
        file_url = f"https://api.telegram.org/file/bot{config.tg_bot.token}/{file_path}"
        response = requests.get(file_url)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f'bot/external_services/voices/{now_str}_voice.{file_ext}', 'wb') as file:
            file.write(response.content)

        with open(f"bot/external_services/voices/{now_str}_voice.{file_ext}", "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        os.remove(f"bot/external_services/voices/{now_str}_voice.{file_ext}")
        return transcript.text
    # def __del__(self):
    #     print(self.__dict__)
    #     print(f"Объект {self} удален ")



    ###########################-------------------СТАРАЯ РЕАЛИЗАЦИЯ ЗАПРОСОВ К OPENAI--------------------------#####################

    # async def connect_client():
    #     client = OpenAI(
    #         organization=config.open_ai.organization_id,
    #         api_key=config.open_ai.api_key
    #     )
    #     #print(f"Подключились к клиенту: {client}")
    #     return client
    #
    #
    # async def create_assistant():
    #     assistant = config.open_ai.assistant_id
    #     #print(f"Подключили ассистента: {assistant}")
    #     return assistant
    #
    #
    # async def create_thread(client):
    #     thread = client.beta.threads.create()
    #     #print(f"Создали тред: {thread.id}")
    #     return thread
    #
    #
    # async def add_message_to_thread(client, thread, content):
    #     client.beta.threads.messages.create(
    #         thread_id=thread.id,
    #         role="user",
    #         content=content
    #     )
    #
    #
    # async def run_assistant(client, thread, assistant):
    #     run = client.beta.threads.runs.create(
    #         thread_id=thread.id,
    #         assistant_id=assistant
    #     )
    #     #print(f"Run ассистент: {run}")
    #     return run
    #
    #
    # async def retrieve_run(client, thread, run):
    #     run_info = client.beta.threads.runs.retrieve(
    #         thread_id=thread.id,
    #         run_id=run.id
    #     )
    #     #print(run_info)
    #     return run_info.status
    #
    #
    # async def wait_run_assistant(client, thread, run):
    #     status = run.status  # начальный статус
    #     while status != 'completed':
    #         # Ожидание 3 секунды перед следующей попыткой
    #         await asyncio.sleep(3)
    #         status = await retrieve_run(client, thread, run)
    #     return status
    #
    #
    # async def response_gpt(client, thread):
    #     return client.beta.threads.messages.list(thread_id=thread.id).data[0].content[0].text.value
    #
    #
    # async def clear_context(client, thread):
    #     client.beta.threads.delete(thread.id)
    #
    #
    # async def recognise_audio_and_voice(client, file_path, file_ext) -> str: #bot: Bot
    #     #print(f"Подключились к клиенту: {client}")
    #     file_url = f"https://api.telegram.org/file/bot{config.tg_bot.token}/{file_path}"
    #     response = requests.get(file_url)
    #     now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #     with open(f'bot/external_services/voices/{now_str}_voice.{file_ext}', 'wb') as file:
    #         file.write(response.content)
    #
    #     with open(f"bot/external_services/voices/{now_str}_voice.{file_ext}", "rb") as audio_file:
    #         transcript = client.audio.transcriptions.create(
    #             model="whisper-1",
    #             file=audio_file
    #         )
    #     os.remove(f"bot/external_services/voices/{now_str}_voice.{file_ext}")
    #     print(transcript)
    #     return transcript.text