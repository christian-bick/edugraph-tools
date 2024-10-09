import typing
from functools import reduce
from re import finditer

from enum import Enum

from semantic import *
import google.generativeai as gemini
import os

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def list_as_words(list):
    return reduce(lambda a, b: a + ' ' +b, list).strip()

def entity_full_name(name):
    name_list = camel_case_split(name)
    name_words = list_as_words(name_list)
    return name_words

def describe_content(file):
    model = gemini.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are presented with learning material that you shall describe as accurately as possible."
    )
    uploaded_file = gemini.upload_file(path=file)

    prompt = """Describe the content in this file"""

    result = model.generate_content(
        [uploaded_file, prompt], generation_config=gemini.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=250,
    ))
    return result.text

def entities_as_enum(entities):
    skill_map = {entity.name: entity_full_name(entity.name) for entity in entities}
    return Enum('SkillEnum', skill_map)


def classify_description(description, parent, entities):
    model = gemini.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are presented with descriptions of learning material that you shall classify."
    )

    skill_dict = {entity.name: entity_full_name(entity.name) for entity in entities}
    SkillEnum = Enum('SkillEnum', skill_dict)

    parent_full_name = entity_full_name(parent.name)

    prompt = """
                Consider the following description of learning material: {0}
    
                Determine the closest area of {1} from the given selection
            """.format(description, parent_full_name)

    result = model.generate_content(
        prompt, generation_config=gemini.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=250,
            response_mime_type="text/x.enum",
            response_schema=SkillEnum
        ))
    return result.text

def classify_description_rec(description, parent, entities):
    classification_value = classify_description(description, parent, entities)

    reverse_skill_dict = {entity_full_name(entity.name): entity.name for entity in entities}
    classification_key = reverse_skill_dict.get(classification_value)

    new_parent = getattr(onto, classification_key)
    new_entities = new_parent.INDIRECT_hasPart
    has_next_level = isinstance(new_entities, list) and len(new_entities) > 0

    if has_next_level:
        classify_description_rec(description, new_parent, new_entities)

    return new_parent


def classify_content(file, parent, entities):
    description = describe_content(file)
    classification = classify_description_rec(description, parent, entities)
    return classification

parent = onto.Mathematics
entities = parent.INDIRECT_hasPart

final_classification = classify_content("./../examples/LongMultiplication-01.png", parent, entities)
print(final_classification)