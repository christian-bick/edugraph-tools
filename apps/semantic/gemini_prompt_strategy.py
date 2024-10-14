import google.generativeai as gemini
import json
import os

from semantic.ontology_util import OntologyUtil

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

system_instruction = """
You are presented with learning material that you shall classify using a given taxonomy.

The taxonomy will always consist of two parts, an outline and definition section. 

Here is an example of a taxonomy for gastronomic terms:

---
Taxonomy of Gastronomy

A) Outline

1 Drinks
1.1 Non-alcoholic Drinks
1.2 Alcoholic Drinks
1.2.1 Beer
1.2.2 Wine
2 Food
2.1 Italian
2.2 French

B) Definitions

1 Drinks

Beverages.

1.1 Non-alcoholic

Beverages without alcohol.

1.2.1 Beer 

A malty alcoholic drink

1.2.2 Wine

An alcoholic drink made of grapes

2 Food

2.1 Italian

Food typically prepared in Italy

2.2 French

Food typically prepared in France
---

The hierarchy of terms in the outline expresses a "part of" relationship. In the example, beer is part of alcoholic 
beverages and alcoholic beverages are part of drinks. Use this hierarchy to find the most specific classification 
matches.

Sometimes, terms in the outline are defined in definition section. When available, use these definitions when 
determining classification matches.
"""

class GeminiPromptStrategy:

    def __init__(self, gemini_file):
        self.gemini_file = gemini_file

    def find_best_match(self, taxonomy, descriptor_type):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        descriptor_type_name = OntologyUtil.natural_name_of_entity(descriptor_type)

        prompt = ("""
                    Consider the following taxonomy:
    
                    {0}
                    
                    Describe the provided file using the following pattern:
                    
                    {2}
    
                    Then find the most accurate {1} that matches the describe learning material, 
                    only using {1}s that were defined in the taxonomy.
    
                    Do not return the description.
                    Return the single best match without its outline number.
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
            system_instruction=system_instruction
        )

        descriptor_type_name = OntologyUtil.natural_name_of_entity(descriptor_type)

        prompt = ("""
                    Consider the following taxonomy:
    
                    {0}
                    
                    Describe the provided file using the following pattern:
                    
                    {2}
    
                    Then find accurately matching {1}s for the described learning material,
                    only using {1}s that were defined in the taxonomy.
    
                    Do not return the description.
                    Return the best matches without their outline number.
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