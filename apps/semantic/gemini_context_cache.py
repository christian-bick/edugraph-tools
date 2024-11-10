import datetime

import google.generativeai as gemini
from google.generativeai import caching


class GeminiContextCache:
    def __init__(self, name, model, system_instruction, content):
        self.name = name
        self.system_instruction = system_instruction
        self.content = content
        self.model = model

    def get(self):
        try:
            return self.__retrieve()
        except Exception as e:
            return self.__build()

    def __retrieve(self):
        return gemini.caching.CachedContent.get(self.name)

    def __build(self):
        return caching.CachedContent.create(
            model=self.model,
            display_name=self.name,  # used to identify the cache
            system_instruction=self.system_instruction,
            contents=self.content,
            ttl=datetime.timedelta(minutes=60),
        )
