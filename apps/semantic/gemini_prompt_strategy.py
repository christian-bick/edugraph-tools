import google.generativeai as gemini
import json
import os

from semantic.ontology_helper import OntologyHelper

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])

class GeminiPromptStrategy:

    def __init__(self, gemini_file):
        self.gemini_file = gemini_file

    def describe_content(self):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are presented with learning material that you shall describe as accurately as possible."
        )

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
            [self.gemini_file, prompt], generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=2000,
            ))
        return result.text

    def find_best_match(self, description, context, descriptor_type):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are presented with descriptions of learning material that you shall classify."
        )

        descriptor_type_name = OntologyHelper.id_as_name(descriptor_type.name)

        prompt = ("""
                    Consider the following taxonomy:
    
                    {0}
    
                    Consider the following description of learning material
    
                    {1}
    
                    Find the most accurate {2} that matches the describe learning material, 
                    * only using terminology that was defined in the taxonomy
                    * preferring low-level {2}s over high-level {2}s 
    
                    Only return the best match without chapter number
                """.format(context, description, descriptor_type_name))

        result = model.generate_content(
            prompt, generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=list[str]
            ))
        result_list = json.loads(result.text)
        return result_list

    def find_matches(self, description, context, descriptor_type):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are presented with descriptions of learning material that you shall classify."
        )

        descriptor_type_name = OntologyHelper.id_as_name(descriptor_type.name)

        prompt = ("""
                    Consider the following taxonomy:
    
                    {0}
    
                    Consider the following description of learning material
    
                    {1}
    
                    Find the applicable {2}s for the described learning material,
                    * only using terminology that was defined in the taxonomy
                    * only using the conditions as defined in the taxonomy
                    * preferring low-level {2}s over high-level {2}s 
    
                    Return matched results without their chapter numbers
                """.format(context, description, descriptor_type_name))

        result = model.generate_content(
            prompt, generation_config=gemini.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=250,
                response_mime_type="application/json",
                temperature=0,
                response_schema=list[str]
            ))
        result_list = json.loads(result.text)
        return result_list