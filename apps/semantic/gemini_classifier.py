from semantic.gemini_file_storage import GeminiFileStorage
from semantic.gemini_prompt_strategy import GeminiPromptStrategy
from semantic.gimini_context_builder import ContextBuilder
from semantic.ontology_helper import OntologyHelper

class GeminiClassifier:

    def __init__(self, onto, ClassifierStrategy = GeminiPromptStrategy):
        self.onto = onto
        self.onto_helper = OntologyHelper(onto)
        self.context_builder = ContextBuilder()
        self.ClassifierStrategy = ClassifierStrategy

    def classify_area(self, classifier):
        descriptor_type = self.onto.Area
        nodes = [ self.onto.Mathematics ]
        context = self.context_builder.build_area_context(nodes)
        area = classifier.find_best_match(context, descriptor_type)
        return area

    def classify_ability(self, classifier):
        descriptor_type = self.onto.Ability
        nodes = [self.onto.AnalyticalCapability]
        context = self.context_builder.build_ability_context(nodes)
        matched_areas = classifier.find_matches(context, descriptor_type)
        return matched_areas

    def classify_scope(self, classifier):
        descriptor_type = self.onto.Scope
        nodes = [self.onto.RepresentationalScope, self.onto.AbstractionScope, self.onto.MeasurementScope]
        context = self.context_builder.build_scope_context(nodes)
        matched_scopes = classifier.find_matches(context, descriptor_type)
        return matched_scopes

    def classify_content(self, file):
        gemini_file = GeminiFileStorage.upload(file)
        classifier = self.ClassifierStrategy(gemini_file)
        classification = {
            "area": self.classify_area(classifier),
            "abilities": self.classify_ability(classifier),
            "scopes": self.classify_scope(classifier)
        }
        return classification

