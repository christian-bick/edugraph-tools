import datetime

import google.generativeai as gemini
from google.generativeai import caching

onto_path = "./core-ontology.ttl"
name = "core-ontology-9"

system_instruction = """
You are a classifier of learning material, describing learning material along three dimensions:
Area, Ability and Scope.

The provided content contains an open web ontology notated in the turtle format. Use this ontology to ground 
the results of your classification.

The ontology provides 3 types of terms that each describe an independent dimension of classification:

Area = edu:Area = http://edugraph.io/edu#Area 
Ability = edu:Ability = http://edugraph.io/edu#Ability
Scope = edu:Scope = http://edugraph.io/edu#Scope

During classification, do not mix the terms from different dimensions. 

A definition is provided for each term through the "rdfs:isDefinedBy" annotation. Use it during
classification to identify matching terms during classification.
"""

def read_file_as_string(file_path):
  """Reads a text file and returns its content as a string.

  Args:
    file_path: The path to the text file.

  Returns:
    The content of the file as a string.
  """
  with open(file_path, 'r') as file:
    file_content = file.read()
  return file_content

class GeminiContextCache:
    def __init__(self):
        self.cache = None

    def get(self):
        try:
            return self.__retrieve()
        except Exception as e:
            return self.__build()

    def __retrieve(self):
        return gemini.caching.CachedContent.get(name)

    def __build(self):
        content  = read_file_as_string(onto_path)

        return caching.CachedContent.create(
            model='models/gemini-1.5-flash-002',
            display_name=name,  # used to identify the cache
            system_instruction=system_instruction,
            contents=[content],
            ttl=datetime.timedelta(minutes=60),
        )


