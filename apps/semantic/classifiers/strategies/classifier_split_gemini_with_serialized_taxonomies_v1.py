import json
import typing

from google import genai
from google.genai import types

from semantic.classifiers.context_builder import build_taxonomy
from semantic.ontology_util import entity_name_of_natural_name, OntologyUtil

system_instruction = """
You are presented with learning material that you shall classify using a given taxonomy.

You will know that a taxonomy starts when you see the line:

Taxonomy for <placeholder>

The taxonomy will always consist of two parts, an outline and definition section. 

You will know that the outline starts when you see the line:

A) Outline of <placeholder>

You will know that the definitions starts when you see the line:

b) Definitions of <placeholder>

Between the "---" is an example of an outline for gastronomic terms :

---
1 Drinks
1.1 Non-alcoholic
1.2 Alcoholic
1.2.1 Beer
1.2.2 Wine
2 Food
2.1 Italian
2.2 French
---

Each item in the outline consists of an index and the term, consequently:

* "1 Drinks" describes the term "Drinks" at index "1"
* "1.1 Non-alcoholic" describes the term "Non-alcoholic" at index "1.1"

Further, the index in the outline express a parent-child relationship, consequently:

* "1.1" and "1.2" are children of "1" and
* "1.2.1" and "1.2.2" are children of "1.2"
* "Alcoholic" is a child element of "Drinks". 
* "Food" is a parent element of "Italian" and "French"
* "Drinks" and "Food" are root elements
* "Beer", "Wine", "Italian" and "French" are leaf elements

Between the "---" is an example of definitions for gastronomic terms :

---
1 Drinks

All types of beverages.

1.1 Non-alcoholic

Beverages without alcohol.

1.2 Alcoholic

Beverages that contain alcohol.

1.2.1 Beer 

A malty alcoholic drink.

1.2.2 Wine

An alcoholic drink made of grapes.

2 Food

2.1 Italian

Dishes that are typically prepared in Italy.

2.2 French

Dishes that are typically prepared in France.
---

Each definition has a title and a description. The title always starts with an index and always exactly matches an item in the previously explained outline. The descriptions follows in the next following paragraphs and ends with the next title.

Consequently:

* "1 Drinks" is the title with index "1" for term "Drinks"
* "All types of beverages." is the description of "Drinks"
* "1.2 Alcoholic" is the title with index "1.2" for term "Alcoholic"
* "Beverages that contain alcohol." is the description of "Alcoholic"

Sometimes, a definition does not contain a description. However when available, use the description when determining classification matches.
"""

single_prompt = """
Step 1: {1}

Step 2: Consider the following taxonomy within "---" for classification:

---
{0}
---

Step 3: Only using terms from the taxonomy, {2}. When responding the matched term, respond without its index and description.
"""

multi_prompt = """
Step 1: {1}
                    
Step 2: Consider the following taxonomy within "---" for classification:

---
{0}
---

Step 3: Only using terms from the taxonomy, {2}. When responding the matched terms, respond without their index and description.
"""


class PromptSingleResponse(typing.TypedDict):
    step_1: str
    step_3: str


class PromptMultiResponse(typing.TypedDict):
    step_1: str
    step_3: list[str]


class ClassifierSplitGeminiWithSerializedTaxonomiesV1:

    def __init__(self, onto):
        onto_util = OntologyUtil(onto)
        self.model = 'gemini-2.0-flash'
        self.client = genai.Client()
        self.area_taxonomy = build_taxonomy("Areas", onto_util.list_root_entities(onto.Area))
        self.ability_taxonomy = build_taxonomy("Abilities", onto_util.list_root_entities(onto.Ability))
        self.scope_taxonomy = build_taxonomy("Scopes", onto_util.list_root_entities(onto.Scope))

    def __find_best_match(self, taxonomy, priming_instruction, matching_instruction, gemini_file):
        prompt = single_prompt.format(taxonomy, priming_instruction, matching_instruction)
        result = self.client.models.generate_content(
            model=self.model,
            contents=[gemini_file, prompt],
            config=types.GenerateContentConfig(
                candidate_count=1,
                temperature=0,
                response_mime_type="application/json",
                response_schema=PromptSingleResponse,
            )
        )
        result_obj = json.loads(result.text)
        return [result_obj['step_3']]

    def __find_matches(self, taxonomy, priming_instruction, matching_instruction, gemini_file):
        prompt = multi_prompt.format(taxonomy, priming_instruction, matching_instruction)
        result = self.client.models.generate_content(
            model=self.model,
            contents=[gemini_file, prompt],
            config=types.GenerateContentConfig(
                candidate_count=1,
                temperature=0,
                response_mime_type="application/json",
                response_schema=PromptMultiResponse,
            ))
        result_obj = json.loads(result.text)
        return result_obj['step_3']

    def classify_area(self, gemini_file):
        matched_areas = self.__find_best_match(
            taxonomy=self.area_taxonomy,
            priming_instruction="Describe the precise area of learning covered by the provided learning material in one sentence.",
            matching_instruction="find the term that best matches the description provided in step 1",
            gemini_file=gemini_file
        )
        return [entity_name_of_natural_name(natural_name) for natural_name in matched_areas]

    def classify_ability(self, gemini_file):
        matched_abilities = self.__find_matches(
            taxonomy=self.ability_taxonomy,
            priming_instruction="Describe the student abilities challenged by the provided learning material in one sentence.",
            matching_instruction="find the terms that best match the description provided in step 1",
            gemini_file=gemini_file
        )
        return [entity_name_of_natural_name(natural_name) for natural_name in matched_abilities]

    def classify_scope(self, gemini_file):
        matched_scopes = self.__find_matches(
            taxonomy=self.scope_taxonomy,
            priming_instruction="Describe the representative aspects of the learning material in up tp 200 words.",
            matching_instruction="find the terms that best match the description of the learning material",
            gemini_file=gemini_file
        )
        return [entity_name_of_natural_name(natural_name) for natural_name in matched_scopes]
