import typing
import google.generativeai as gemini
import json

class PromptSingleResponse(typing.TypedDict):
    step_1: str
    step_3: str

class PromptMultiResponse(typing.TypedDict):
    step_1: str
    step_3: list[str]

system_instruction = ""
single_prompt = ""
multi_prompt = ""

class SplitPromptStrategyGeminiV2:

    def __init__(self, gemini_file):
        self.gemini_file = gemini_file

    def find_best_match(self, taxonomy, priming_instruction, matching_instruction):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        prompt = single_prompt.format(taxonomy, priming_instruction, matching_instruction)

        result = model.generate_content(
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptSingleResponse
            ))
        result_obj = json.loads(result.text)
        return [ result_obj['step_3'] ]

    def find_matches(self, taxonomy, priming_instruction, matching_instruction):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        prompt = multi_prompt.format(taxonomy, priming_instruction, matching_instruction)

        result = model.generate_content(
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=PromptMultiResponse
            ))
        result_obj = json.loads(result.text)
        return result_obj['step_3']