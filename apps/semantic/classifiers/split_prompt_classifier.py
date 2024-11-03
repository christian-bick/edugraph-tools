from semantic.ontology_util import entity_name_of_natural_name
from .context_builder import build_taxonomy
from .split_prompt_strategy_gemini import SplitPromptStrategyGemini


class SplitPromptClassifier:

    def __init__(self, onto):
        self.onto = onto
        self.ClassifierStrategy = SplitPromptStrategyGemini

    def classify_area(self, classifier):
        entities = [ self.onto.Mathematics ]
        taxonomy = build_taxonomy("Areas", entities)
        matched_areas = classifier.find_best_match(
            taxonomy=taxonomy,
            priming_instruction="Describe the precise area of learning covered by the provided learning material in one sentence.",
            matching_instruction="find the term that best matches the description provided in step 1"
        )
        return [ entity_name_of_natural_name(natural_name) for natural_name in matched_areas ]

    def classify_ability(self, classifier):
        entities = [self.onto.AnalyticalCapability]
        taxonomy = build_taxonomy("Abilities", entities)
        matched_abilities = classifier.find_matches(
            taxonomy=taxonomy,
            priming_instruction="Describe the student abilities challenged by the provided learning material in one sentence.",
            matching_instruction="find the terms that best match the description provided in step 1"
        )
        return [ entity_name_of_natural_name(natural_name) for natural_name in matched_abilities ]

    def classify_scope(self, classifier):
        entities = [self.onto.RepresentationalScope, self.onto.AbstractionScope, self.onto.MeasurementScope]
        taxonomy = build_taxonomy("Scopes", entities)
        matched_scopes = classifier.find_matches(
            taxonomy=taxonomy,
            priming_instruction="Describe the representative aspects of the learning material in up tp 500 words.",
            matching_instruction="find the terms that best match the description of the learning material"
        )
        return [ entity_name_of_natural_name(natural_name) for natural_name in matched_scopes ]

    def classify_content(self, file):
        classifier = self.ClassifierStrategy(file)
        classification = {
            "areas": self.classify_area(classifier),
            "abilities": self.classify_ability(classifier),
            "scopes": self.classify_scope(classifier)
        }
        return classification
