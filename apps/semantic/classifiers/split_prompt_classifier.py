from .context_builder import build_taxonomy
from semantic import OntologyUtil


class SplitPromptClassifier:

    def __init__(self, onto, ClassifierStrategy):
        self.onto = onto
        self.ClassifierStrategy = ClassifierStrategy

    def classify_area(self, classifier):
        descriptor_type = self.onto.Area
        entities = [ self.onto.Mathematics ]
        context = build_taxonomy("Areas", entities)
        matched_areas = classifier.find_best_match(context, descriptor_type)
        return [ OntologyUtil.entity_name_of_natural_name(natural_name) for natural_name in matched_areas ]

    def classify_ability(self, classifier):
        descriptor_type = self.onto.Ability
        entities = [self.onto.AnalyticalCapability]
        context = build_taxonomy("Abilities", entities)
        matched_abilities = classifier.find_matches(context, descriptor_type)
        return [ OntologyUtil.entity_name_of_natural_name(natural_name) for natural_name in matched_abilities ]

    def classify_scope(self, classifier):
        descriptor_type = self.onto.Scope
        entities = [self.onto.RepresentationalScope, self.onto.AbstractionScope, self.onto.MeasurementScope]
        context = build_taxonomy("Scopes", entities)
        matched_scopes = classifier.find_matches(context, descriptor_type)
        return [ OntologyUtil.entity_name_of_natural_name(natural_name) for natural_name in matched_scopes ]

    def classify_content(self, file):
        classifier = self.ClassifierStrategy(file)
        classification = {
            "areas": self.classify_area(classifier),
            "abilities": self.classify_ability(classifier),
            "scopes": self.classify_scope(classifier)
        }
        return classification
