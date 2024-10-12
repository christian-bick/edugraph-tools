import google.generativeai as gemini
import json
import os

from semantic.ontology_util import OntologyUtil

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

description_template = """
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

class GeminiPromptStrategy:

    def __init__(self, gemini_file):
        self.gemini_file = gemini_file

    def find_best_match(self, taxonomy, descriptor_type):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are presented with learning material that you shall classify."
        )

        descriptor_type_name = OntologyUtil.entity_native_name(descriptor_type)

        prompt = ("""
                    Consider the following taxonomy:
    
                    {0}
                    
                    Describe the provided file using the following pattern:
                    
                    {2}
    
                    Then find the most accurate {1} that matches the describe learning material, 
                    * only using terminology that was defined in the taxonomy
                    * preferring low-level {1}s over high-level {1}s 
    
                    Do not return the description.
                    Return the single best match without chapter number.
                """.format(taxonomy, descriptor_type_name, description_template))

        result = model.generate_content(
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=list[str]
            ))
        result_list = json.loads(result.text)
        return result_list

    def find_matches(self, taxonomy, descriptor_type):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are presented with learning material that you shall classify."
        )

        descriptor_type_name = OntologyUtil.entity_native_name(descriptor_type)

        prompt = ("""
                    Consider the following taxonomy:
    
                    {0}
                    
                    Describe the provided file using the following pattern:
                    
                    {2}
    
                    Then find the applicable {1}s for the described learning material,
                    * only using terminology that was defined in the taxonomy
                    * only using the conditions as defined in the taxonomy
                    * preferring low-level {1}s over high-level {1}s 
    
                    Do not return the description.
                    Return matched results without their chapter numbers.
                """.format(taxonomy, descriptor_type_name, description_template))

        result = model.generate_content(
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=list[str]
            ))
        result_list = json.loads(result.text)
        return result_list