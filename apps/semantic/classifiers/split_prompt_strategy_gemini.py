import google.generativeai as gemini
import json

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
* "Drinks" and "Food" root elements
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

Each definition has a title and a description. The title always starts with an index and always exactly matches an 
item in the previously explained outline. The descriptions follows in the next following paragraphs and ends with 
the next title.

Consequently:

* "1 Drinks" is the title with index "1" for term "Drinks"
* "All types of beverages." is the description of "Drinks"
* "1.2 Alcoholic" is the title with index "1.2" for term "Alcoholic"
* "Beverages that contain alcohol." is the description of "Alcoholic"

Sometimes, a definition does not contain a description. However when available, use the description when 
determining classification matches. Otherwise, use the best description available to you.
"""

class SplitPromptStrategyGemini:

    def __init__(self, gemini_file):
        self.gemini_file = gemini_file

    def find_best_match(self, taxonomy, description_instruction):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        prompt = ("""
                    1) For the provided file: {1}
                    
                    2) Consider the following taxonomy of entities within "---":
                    
                    ---
                    {0}
                    ---
                    
                    3) Find the term that best matches the description of the learning material. Try to be as
                    specific as possible.
                     
                    4) Only return the matched term, without index and description.
                """.format(taxonomy, description_instruction))

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

    def find_matches(self, taxonomy, description_instruction):
        model = gemini.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

        prompt = ("""
                    1) For the provided file: {1}
                    
                    2) Consider the following taxonomy of entities within "---":
    
                    ---
                    {0}
                    ---
                    
                    3) Find the terms that best match the description of the learning material. Try to be as
                    specific as possible.
    
                    4) Only return the matched terms, without index and description.
                """.format(taxonomy, description_instruction))

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