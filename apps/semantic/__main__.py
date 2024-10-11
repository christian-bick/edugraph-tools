
import google.generativeai as gemini
import os

from owlready2 import get_ontology

from semantic.gemini_classifier import GeminiClassifier

from semantic.gemini_prompt_strategy import GeminiPromptStrategy

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])








description = """
**Type of learning material:** 

This is a digital image of what appears to be a printed learning material, likely a poster or a page from a workbook.

**Content description:**

The image shows a method for performing long multiplication with the problem 524 x 381. It breaks down the multiplication process into four color-coded steps:

1. **Multiply by the units digit (purple):** 524 is multiplied by 1.
2. **Multiply by the tens digit (blue):** 524 is multiplied by 8, and a 0 is placed in the units column of the result (41920) to account for the place value.
3. **Multiply by the hundreds digit (green):** 524 is multiplied by 3, and two 0s are placed in the units and tens columns of the result (157200) to account for the place value.
4. **Add the partial products:** The results from the previous steps (524, 41920, and 157200) are added together to get the final answer (199644).

The example uses color-coding to highlight the different steps and the corresponding digits in the multiplier (381). Arrows visually connect the steps and their outcomes.

**Used forms of representation:**

* **Text:** Explanations, instructions, and the problem itself.
* **Numbers:** The example multiplication problem.
* **Color-coding:** To highlight different steps and parts of the problem.
* **Arrows:** To visually connect steps and their outcomes.
* **Spatial organization:** Clear layout with distinct sections for the problem, steps, and explanations.

**Field and area of learning:**

This material falls under the field of **mathematics**, specifically **arithmetic** and **multiplication**.

**Learning abilities:**

The material primarily utilizes **logical reasoning** and **procedural skills**. It requires the learner to follow a sequence of steps, understand place value, and perform arithmetic operations accurately.

**Intention behind the learning material:**

The intention is to provide a clear and step-by-step guide to long multiplication for numbers that are not easily multiplied mentally. The use of visual aids and color-coding aims to make the process easier to understand and remember.

**Other observations:**

* The visual appeal and clear layout likely contribute to a positive learning experience.
* The material implicitly encourages deeper mathematical thinking by demonstrating the underlying principles of place value and the distributive property in multiplication.
* While the example focuses on whole numbers, the method can be generalized to multiplication with decimals.
"""

##classification = classify_text(description)
#print(classification)



onto = get_ontology("./../core-ontology.rdf").load()
onto.base_iri = "http://edugraph.io/edu#"

example_file = "./../examples/LongMultiplication-01.png"

classifier = GeminiClassifier(onto, GeminiPromptStrategy)
result = classifier.classify_content(example_file)

print(result)