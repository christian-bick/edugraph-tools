import datetime

from linecache import cache

import google.generativeai as gemini
from google.generativeai import caching

onto_path = "./core-ontology.ttl"
name = "core-ontology-1"

class GeminiContextCache:
    def __init__(self):
        self.cache = None

    def get(self):
        if cache is not None:
            return self.__build()
        else:
            try:
                return self.__retrieve()
            except():
                return self.__build()

    def __retrieve(self):
        self.cache = gemini.caching.CachedContent.get(name)
        return self.cache

    def __build(self):
        file = gemini.upload_file(mime_type="text/plain", path=onto_path)
        self.cache = caching.CachedContent.create(
            model='models/gemini-1.5-flash-001',
            display_name=name,  # used to identify the cache
            system_instruction=(
                'You are an expert video analyzer, and your job is to answer '
                'the user\'s query based on the video file you have access to.'
            ),
            contents=[file],
            ttl=datetime.timedelta(minutes=60),
        )
        return self.cache


