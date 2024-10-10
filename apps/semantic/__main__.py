import json
import typing
from functools import reduce
from lib2to3.fixes.fix_input import context
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

    prompt = """Describe the provided file using the following pattern:
    
        Type of learning material:
        
        <Description of its physical or digital nature in 1 sentence>
        
        Content description:
        
        <For text files, a summary of the text, for pictures, a description of the picture, using up to 
        500 words>
        
        Used forms of representation:
        
        <Description of different forms of representation in up to 5 bullet points>
        
        Field and area of learning:
        
        <Describe the field and area of learning in 1-2 sentences>
        
        <Describe the main learning abilities used when interacting with the material in 1-3 sentence>
        
        <Describe the intention behind the learning material>
        
        Other observations:
        
        <Optionally add other significant observations about the learning material>
    """

    result = model.generate_content(
        [uploaded_file, prompt], generation_config=gemini.types.GenerationConfig(
        candidate_count=1,
        max_output_tokens=2000,
    ))
    return result.text

def entities_as_enum(entities):
    skill_map = {entity.name: id_as_name(entity.name) for entity in entities}
    return Enum('SkillEnum', skill_map)


def classify_description(description, context, descriptor_type, descriptor_node, descriptor_parts):
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
    
                Determine the closest {1} of {2} from the given selection using the following taxonomy:
                
                {3}
            """.format(description, descriptor_type_name, descriptor_node_name, context)

    result = model.generate_content(
        prompt, generation_config=gemini.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=250,
            temperature=0,
            response_mime_type="text/x.enum",
            response_schema=DescriptorEnum,
        ))
    return result.text

def find_matches(description, context, descriptor_type):
    model = gemini.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are presented with descriptions of learning material that you shall classify."
    )

    descriptor_type_name = id_as_name(descriptor_type.name)

    prompt = ("""
                Consider the following taxonomy:

                {0}
                
                Consider the following description of learning material
                
                {1}
                
                Find the applicable {2}s for the described learning material,
                * only using terminology that was defined in the taxonomy
                * only using the conditions as defined in the taxonomy
                * only when you are certain about your judgement
                
                Return matched results without their chapter numbers
            """.format(context, description, descriptor_type))

    result = model.generate_content(
        prompt, generation_config=gemini.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=250,
            response_mime_type="application/json",
            temperature=0,
            response_schema=list[str]
        ))
    result_list = json.loads(result.text)
    return [node_of_value(value) for value in result_list]

def is_leaf_entity(node):
    children = node.INDIRECT_hasPart
    return not (isinstance(children, list) and len(children) > 0)

def node_of_value(value):
    classification_key = value.replace(" ", "")
    return getattr(onto, classification_key)

def classify_description_rec(description, context, descriptor_type, descriptor_node):
    if is_leaf_entity(descriptor_node):
        return descriptor_node

    descriptor_parts = descriptor_node.INDIRECT_hasPart
    classification_value = classify_description(description, context, descriptor_type, descriptor_node, descriptor_parts)

    new_descriptor_node = node_of_value(classification_value)

    return classify_description_rec(description, context, descriptor_type, new_descriptor_node)

def collect_leafs(descriptor_node):
    if is_leaf_entity(descriptor_node):
        return [ descriptor_node ]


    descriptor_parts = descriptor_node.INDIRECT_hasPart
    leaves = reduce(lambda tail, head: collect_leafs(head) + tail, descriptor_parts, [])
    return leaves

def cluster_nodes(nodes):
    clusters = defaultdict(list)
    for node in nodes:
        parent_node = node.INDIRECT_partOf[0]
        key = parent_node.name
        clusters[key].append(node)
    return clusters

def list_parents(nodes):
    leaf_parents = {}
    for node in nodes:
        parent_node = node.INDIRECT_partOf[0]
        key = parent_node.name
        leaf_parents[key] = parent_node
    return leaf_parents.values()

def hierarchy_to_string(hierarchy):
    level_string = reduce(lambda tail, head: tail + str(head) + '.', hierarchy, "")
    return level_string[:-1]

def expand_context(hierarchy, node):

    definition = node.isDefinedBy

    added_context = hierarchy_to_string(hierarchy) + ' ' + id_as_name(node.name)

    if isinstance(definition, list) and len(definition) > 0:
        added_context += "\n\n{0}".format(definition[0])

    added_context += "\n\n"
    return added_context

def expand_context_level(hierarchy, context, nodes):
    current_index = len(hierarchy)-1
    current_counter = 1
    for node in nodes:
        hierarchy[current_index] = current_counter
        context += expand_context(hierarchy, node)

        if not is_leaf_entity(node):
            descriptor_parts = node.INDIRECT_hasPart
            new_hierarchy = hierarchy + [1]
            context = expand_context_level(new_hierarchy, context, descriptor_parts)

        current_counter = current_counter + 1

    return context

def classify_area(description):
    descriptor_type = onto.Area
    descriptor_node = onto.Mathematics
    context = build_area_context()
    area = classify_description_rec(description, context, descriptor_type, descriptor_node)
    return area

def classify_ability(description):
    descriptor_type = onto.Ability
    context = "Taxonomy of Abilities\n\n"
    context += build_ability_context()
    matched_areas = find_matches(description, context, descriptor_type)
    return matched_areas

def classify_scope(description):
    descriptor_type = onto.Scope
    context = "Taxonomy of Scopes\n\n"
    context += build_scope_context()
    matched_scopes = find_matches(description, context, descriptor_type)
    return matched_scopes

def build_ability_context():
    return expand_context_level([1], "", [onto.AnalyticalCapability])

def build_scope_context():
    return expand_context_level([1], "",[onto.RepresentationalScope, onto.AbstractionScope, onto.MeasurementScope])

def build_area_context():
    return expand_context_level([1], "",[onto.Mathematics])

def classify_content(file):
    description = describe_content(file)
    return classify_text(description)

def classify_text(text):
    classification = {
        "area": classify_area(text),
        "abilities": classify_ability(text),
        "scopes": classify_scope(text)
    }
    return classification

file = "./../examples/LongMultiplication-01.png"

description = """
**Type of learning material:** 

This is a digital image of what appears to be a printed learning material, likely a poster or a page from a workbook.

**Content description:**

The image shows a method for performing long multiplication with the problem 524 x 381. It breaks down the multiplication process into four color-coded steps:

1. **Multiply by the units digit (purple):** 524 is multiplied by 1.
2. **Multiply by the tens digit (blue):** 524 is multiplied by 8, and a 0 is placed in the units column of the result (41920) to account for the place value.
3. **Multiply by the hundreds digit (green):** 524 is multiplied by 3, and two 0s are placed in the units and tens columns of the result (157200) to account for the place value.
4. **Add the partial products:** The results from the previous steps (524, 41920, and 157200) are added together to get the final answer (199644).

The example uses color-coding to highlight the different steps and the corresponding digits in the multiplier (381). Arrows visually connect the steps and their outcomes.

**Used forms of representation:**

* **Text:** Explanations, instructions, and the problem itself.
* **Numbers:** The example multiplication problem.
* **Color-coding:** To highlight different steps and parts of the problem.
* **Arrows:** To visually connect steps and their outcomes.
* **Spatial organization:** Clear layout with distinct sections for the problem, steps, and explanations.

**Field and area of learning:**

This material falls under the field of **mathematics**, specifically **arithmetic** and **multiplication**.

**Learning abilities:**

The material primarily utilizes **logical reasoning** and **procedural skills**. It requires the learner to follow a sequence of steps, understand place value, and perform arithmetic operations accurately.

**Intention behind the learning material:**

The intention is to provide a clear and step-by-step guide to long multiplication for numbers that are not easily multiplied mentally. The use of visual aids and color-coding aims to make the process easier to understand and remember.

**Other observations:**

* The visual appeal and clear layout likely contribute to a positive learning experience.
* The material implicitly encourages deeper mathematical thinking by demonstrating the underlying principles of place value and the distributive property in multiplication.
* While the example focuses on whole numbers, the method can be generalized to multiplication with decimals.
"""

##classification = classify_text(description)
#print(classification)

result = classify_text(description)

print(result)