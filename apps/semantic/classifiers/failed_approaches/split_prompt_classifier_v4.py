import typing
import google.generativeai as gemini
import json


class PromptResponse(typing.TypedDict):
    Area: list[str]
    Ability: list[str]
    Scope: list[str]


prompt = """
Classify the learning material in the given image file and return the matching descriptors:

Step 1: Describe the learning material's area of education with the best matching term of type "edu:Area"
Step 2: With respect to the area chosen in step 1, find up to 5 terms of type "edu:Ability" that best 
describe how the learning material challenges student abilities.
Step 3: With respect to the area chosen in step 1 and the abilities chosen in step 2, find up to 10 terms of type
"edu:Scope" that best describe the exact scope of the learning material.

- Return exactly one term in the field "Area" from step 1
- Return at least one but no more than 5 terms from step 2
- Return at least one but no more than 10 terms from step 3

- Return the terms without the "edu:" prefix
"""

prompt_2 = """
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
prompt_area = """
Describe the learning material's area of education with the best matching term of type "edu:Area".
Prefer specific terms over general terms.
Return the term without the "edu:" prefix
"""

prompt_ability = """
Describe the student abilities trained by the given learning material with the best matching term of type "edu:Ability"
Return the terms without the "edu:" prefix
"""

prompt_scope = """
Narrow down the exact scope of the learning material with the best matching terms of type "edu:Scope"
Return the terms without the "edu:" prefix
"""


class SplitPromptClassifierV4:

    def __init__(self, cache):
        self.model = gemini.GenerativeModel.from_cached_content(cached_content=cache)

    def classify_content(self, file):
        return {
            'Area': self.__classify(file, prompt_area),
            'Ability': self.__classify(file, prompt_ability),
            'Scope': self.__classify(file, prompt_scope),
        }

    def __classify(self, file, specific_prompt):
        result = self.model.generate_content(
            [file, specific_prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=list[str]
            ))
        print(result.text)
        result_obj = json.loads(result.text)
        return result_obj


