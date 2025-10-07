import json
from datetime import datetime
import time
from openai import OpenAI

from client.openai_client import OpenAIClient


class InferenceService:

    def __init__(self, system_prompt_file_path, user_prompt_file_path):
        self.system_prompt_file_path = system_prompt_file_path
        self.user_prompt_file_path = user_prompt_file_path
        self.openai_client: OpenAI = OpenAIClient().get_client()

    def __get_string_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def do_inference(self, data, metadata):
        start_time = time.time()  # Start timer
        result = {**metadata,
                  "execution_time": datetime.now().astimezone().isoformat()}
        try:
            messages: list = self.__prepare_message_list(data)
            request = {
                "model": "deepseek-chat",
                "messages": messages,
                "stream": False,
                "temperature": 1.0,
                "response_format": {"type": "json_object"}
            }
            result['request'] = request
            response = self.openai_client.chat.completions.create(
                model=request.get("model"),
                messages=request.get("messages"),
                stream=request.get("stream"),
                temperature=request.get("temperature"),
                response_format=request.get("response_format"),
            )
            result['raw_response'] = response.model_dump()
            json_str = response.choices[0].message.content
            result['json_response'] = json.loads(json_str)
            print("Inference completed successfully")
        except Exception as e:
            print(f"Error: {str(e)}")
            result['error'] = {str(e)}
        end_time = time.time()
        result['inference_time'] = end_time - start_time
        return result

    def __prepare_message_list(self, data):
        """PREPARE PROMPT"""
        system_prompt = self.__get_string_from_file(
            self.system_prompt_file_path)
        user_prompt = self.__get_string_from_file(self.user_prompt_file_path)
        user_prompt = user_prompt.replace("{{data}}", data)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

