from functools import reduce
from re import finditer

from enum import Enum

from semantic import *
import google.generativeai as gemini
import os

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])
model = gemini.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are presented with learning material that you shall describe as accurately as possible."
)

start = onto.Arithmetic
entities = start.INDIRECT_hasPart

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def list_as_words(list):
    return reduce(lambda a, b: a + ' ' +b, list).strip()

def entity_full_name(name):
    name_list = camel_case_split(name)
    name_words = list_as_words(name_list)
    return name_words

def define_entity(entity):
    entity_name = entity_full_name(entity.name)

    prompt = """
        Define "{0}"
    """.format(entity_name)

    result = model.generate_content(prompt, generation_config=gemini.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=250,
        temperature=1.5
    ))
    return [ entity, result.text ]

def describe_picture(file):
    uploaded_file = gemini.upload_file(path=file)

    prompt = """Describe the content of this picture"""

    result = model.generate_content(
        [uploaded_file, prompt], generation_config=gemini.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=250,
    ))

    return result.text

def classify_picture(file, entities):
    skill_map = {entity.name: entity_full_name(entity.name) for entity in entities}
    SkillEnum = Enum('SkillEnum', skill_map)

    uploaded_file = gemini.upload_file(path=file)

    prompt = """Execute the following steps:
            1) Describe the content of this picture
            2) Determine the closest area of math from the given selection
        """

    result = model.generate_content(
        [uploaded_file, prompt], generation_config=gemini.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=250,
            response_mime_type="text/x.enum",
            response_schema=SkillEnum
        ))

    print(result.text)
    return result

def query_entities(entities):
    for entity in entities:
        entry = define_entity(entity)
        print(entry)

#query_entities(entities)

classify_picture("./../examples/LongMultiplication-01.png", entities)