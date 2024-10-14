from semantic.gemini_prompt_strategy import GeminiPromptStrategy
from semantic.context_builder import ContextBuilder
from semantic.ontology_util import OntologyUtil


class GeminiClassifier:

    def __init__(self, onto, ClassifierStrategy = GeminiPromptStrategy):
        self.onto = onto
        self.context_builder = ContextBuilder()
        self.ClassifierStrategy = ClassifierStrategy

    def classify_area(self, classifier):
        descriptor_type = self.onto.Area
        nodes = [ self.onto.Mathematics ]
        context = self.context_builder.build_area_context(nodes)
        matched_areas = classifier.find_best_match(context, descriptor_type)
        return [ OntologyUtil.entity_name_of_natural_name(natural_name) for natural_name in matched_areas ]

    def classify_ability(self, classifier):
        descriptor_type = self.onto.Ability
        nodes = [self.onto.AnalyticalCapability]
        context = self.context_builder.build_ability_context(nodes)
        matched_abilities = classifier.find_matches(context, descriptor_type)
        return [ OntologyUtil.entity_name_of_natural_name(natural_name) for natural_name in matched_abilities ]

    def classify_scope(self, classifier):
        descriptor_type = self.onto.Scope
        nodes = [self.onto.RepresentationalScope, self.onto.AbstractionScope, self.onto.MeasurementScope]
        context = self.context_builder.build_scope_context(nodes)
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
