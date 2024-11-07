import typing
import google.generativeai as gemini
import json

from semantic.classifiers.failed_approaches.split_prompt_strategy_gemini_v2 import SplitPromptStrategyGeminiV2

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

class SplitPromptClassifierV2:

    def __init__(self, onto, cache):
        self.onto = onto
        self.ClassifierStrategy = SplitPromptStrategyGeminiV2
        self.cache = cache

    def classify_content(self, file):
        model = gemini.GenerativeModel.from_cached_content(cached_content=self.cache)

        result = model.generate_content(
            [file, prompt_2], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptResponse
            ))
        print(result.text)
        result_obj = json.loads(result.text)
        print(result_obj)
        return result_obj
