import typing

import google.generativeai as gemini
import json

from semantic.gemini_context_cache import GeminiContextCache

def read_file_as_string(file_path):
  with open(file_path, 'r') as file:
    file_content = file.read()
  return file_content

class PromptResponse(typing.TypedDict):
    Area: list[str]
    Ability: list[str]
    Scope: list[str]

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

prompt = """
Classify the learning material in the given image file and return the matching areas, abilities and scope as follows:

Step 1: Describe the learning material's area of education with the best matching term of type "edu:Area"
Step 2: Describe the student abilities trained by the learning material with the best matching terms of type "edu:Ability"
Step 3: Narrow down the exact scope of the learning material with the best matching terms of type "edu:Scope"
Step 4: Return the result as follows
- Return exactly one term in the field "Area" from step 1
- Return at least one but no more than 5 terms in the field "Ability" from step 2
- Return at least one but no more than 10 terms in field "Scope" from step 3
- Return all terms without the "edu:" prefix
"""

class ClassifierUnifiedGeminiWithTurtleTaxonomyV1:

    def __init__(self):
        self.cache = GeminiContextCache(
            name='ontology-1',
            model='models/gemini-1.5-flash-001',
            system_instruction=system_instruction,
            content=[ read_file_as_string(onto_path) ]
        )

    def classify_content(self, file):
        cached_content = self.cache.get()
        model = gemini.GenerativeModel.from_cached_content(cached_content=cached_content)
        result = model.generate_content(
            [prompt, file], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptResponse
            ))
        print(result.text)
        result_obj = json.loads(result.text)
        return result_obj
