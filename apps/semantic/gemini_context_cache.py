import datetime

from linecache import cache

import google.generativeai as gemini
from google.generativeai import caching

onto_path = "./core-ontology.ttl"
name = "core-ontology-2"

system_instruction = """
You are a classifier of learning material, describing learning material along three dimensions:
Area, ability and scope. You are provided with an ontology that is noted in the Web Ontology Language
using the "plain/turtle" mimetype.

The ontology describes 3 dimensions for classification: "Area", "Ability" and "Scope"
which are each organized as hierarchical taxonomies via the inferred "partOf" object property.

Further, the definition for each individual is provided through the "isDefinedBy" annotation. Use both during
you classification efforts to identify the correct terms for classification.
"""

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
            system_instruction=system_instruction,
            contents=[file],
            ttl=datetime.timedelta(minutes=60),
        )
        return self.cache


