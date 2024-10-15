from .context_builder import build_taxonomy
from semantic.ontology_util import entity_name_of_natural_name

class SplitPromptClassifier:

    def __init__(self, onto, ClassifierStrategy):
        self.onto = onto
        self.ClassifierStrategy = ClassifierStrategy

    def classify_area(self, classifier):
        entities = [ self.onto.Mathematics ]
        taxonomy = build_taxonomy("Areas", entities)
        matched_areas = classifier.find_best_match(
            taxonomy=taxonomy,
            description_instruction="Describe the area of learning in one sentence."
        )
        return [ entity_name_of_natural_name(natural_name) for natural_name in matched_areas ]

    def classify_ability(self, classifier):
        entities = [self.onto.AnalyticalCapability]
        context = build_taxonomy("Abilities", entities)
        matched_abilities = classifier.find_matches(
            taxonomy=context,
            description_instruction="Describe the challenged student abilities in one sentence."
        )
        return [ entity_name_of_natural_name(natural_name) for natural_name in matched_abilities ]

    def classify_scope(self, classifier):
        entities = [self.onto.RepresentationalScope, self.onto.AbstractionScope, self.onto.MeasurementScope]
        taxonomy = build_taxonomy("Scopes", entities)
        matched_scopes = classifier.find_matches(
            taxonomy=taxonomy,
            description_instruction="Describe the what the learning material in up to 500 words."
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
