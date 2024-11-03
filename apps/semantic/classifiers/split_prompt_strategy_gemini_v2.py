import typing
import google.generativeai as gemini
import json

class PromptSingleResponse(typing.TypedDict):
    step_1: str
    step_2: str

class PromptMultiResponse(typing.TypedDict):
    step_1: str
    step_2: list[str]

single_prompt = "{0}\n{1}"
multi_prompt = "{0}\n{1}"

class SplitPromptStrategyGeminiV2:

    def __init__(self, model, gemini_file):
        self.gemini_file = gemini_file
        self.model = model

    def find_best_match(self, priming_instruction, matching_instruction):
        prompt = single_prompt.format(priming_instruction, matching_instruction)

        result = self.model.generate_content(
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptSingleResponse
            ))
        result_obj = json.loads(result.text)
        return [ result_obj['step_2'] ]

    def find_matches(self, priming_instruction, matching_instruction):
        prompt = multi_prompt.format(priming_instruction, matching_instruction)

        result = self.model.generate_content(
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptMultiResponse
            ))
        result_obj = json.loads(result.text)
        return result_obj['step_2']