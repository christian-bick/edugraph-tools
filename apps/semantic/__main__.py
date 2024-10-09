import typing
from functools import reduce
from re import finditer

from enum import Enum

from google.protobuf.descriptor import Descriptor

from semantic import *
import google.generativeai as gemini
import os

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def list_as_words(list):
    return reduce(lambda a, b: a + ' ' +b, list).strip()

def id_as_name(name):
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
    skill_map = {entity.name: id_as_name(entity.name) for entity in entities}
    return Enum('SkillEnum', skill_map)


def classify_description(description, descriptor_type, descriptor_node, descriptor_parts):
    model = gemini.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are presented with descriptions of learning material that you shall classify."
    )

    descriptor_dict = {entity.name: id_as_name(entity.name) for entity in descriptor_parts}
    DescriptorEnum = Enum('DescriptorEnum', descriptor_dict)

    descriptor_node_name = id_as_name(descriptor_node.name)
    descriptor_type_name = id_as_name(descriptor_type.name)

    prompt = """
                Consider the following description of learning material: {0}
    
                Determine the closest {1} of {2} from the given selection
            """.format(description, descriptor_type_name, descriptor_node_name)

    result = model.generate_content(
        prompt, generation_config=gemini.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=250,
            response_mime_type="text/x.enum",
            response_schema=DescriptorEnum
        ))
    return result.text

def classify_description_rec(description, descriptor_type, descriptor_node):
    descriptor_parts = descriptor_node.INDIRECT_hasPart
    is_leaf_entity = not (isinstance(descriptor_parts, list) and len(descriptor_parts) > 0)

    if is_leaf_entity:
        return descriptor_node

    classification_value = classify_description(description, descriptor_type, descriptor_node, descriptor_parts)

    reverse_skill_dict = {id_as_name(entity.name): entity.name for entity in descriptor_parts}
    classification_key = reverse_skill_dict.get(classification_value)
    new_descriptor_node = getattr(onto, classification_key)

    return classify_description_rec(description, descriptor_type, new_descriptor_node)


def classify_content(file, descriptor_type, descriptor_node):
    description = describe_content(file)
    classification = classify_description_rec(description, descriptor_type, descriptor_node)
    return classification

descriptor_start_node = onto.Mathematics
descriptor_start_type = onto.Area
file = "./../examples/LongMultiplication-01.png"

final_classification = classify_content(file, descriptor_start_type, descriptor_start_node)
print(final_classification)