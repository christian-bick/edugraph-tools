import typing
import google.generativeai as gemini
import json

from semantic.classifiers.split_prompt_strategy_gemini_v2 import SplitPromptStrategyGeminiV2

class PromptResponse(typing.TypedDict):
    Area: list[str]
    Ability: list[str]
    Scope: list[str]


prompt = """
Classify the following file and return the matching descriptors divided by "Area", "Ability" and "Scope". Return a
single best matching area, the best matching abilities (no more than 5) 
and the best matching matching scopes (no more than 10).
"""

class SplitPromptClassifierV2:

    def __init__(self, onto, cache):
        self.onto = onto
        self.ClassifierStrategy = SplitPromptStrategyGeminiV2
        self.cache = cache

    def classify_content(self, file):
        model = gemini.GenerativeModel.from_cached_content(cached_content=self.cache)
        classifier = self.ClassifierStrategy(model, file)

        result = model.generate_content(
            [file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptResponse
            ))
        result_obj = json.loads(result.text)
        print(result_obj)
        return result_obj
