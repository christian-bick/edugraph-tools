from functools import reduce
from re import finditer

from semantic import *
import google.generativeai as gemini
import os
import typing_extensions as typing

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])
model = gemini.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a lexicon that describes different areas of education"
)

start = onto.Mathematics
entities = start.INDIRECT_hasPart

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def list_as_words(list):
    return reduce(lambda a, b: a + ' ' +b, list).strip()

def entity_full_name(entity):
    name_list = camel_case_split(entity.name)
    name_words = list_as_words(name_list)
    return name_words

def define_entity(entity):
    entity_name = entity_full_name(entity)
    parent_name = entity_full_name(entity.INDIRECT_partOf[0])

    prompt = """
        Define "{0}"
    """.format(entity_name, parent_name)

    print(prompt)

    result = model.generate_content(prompt, generation_config=gemini.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=250,
        temperature=1.5
    ))
    return [ entity, result.text ]

def query_entities(entities):
    for entity in entities:
        entry = define_entity(entity)
        print(entry)

query_entities(entities)