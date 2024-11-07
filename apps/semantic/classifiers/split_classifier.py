from semantic.classifiers.split_classifier_gemini_with_serialized_taxonomies_v1 import \
    SplitClassifierGeminiWithSerializedTaxonomiesV1


class SplitClassifier:

    def __init__(self, onto):
        self.classifier = SplitClassifierGeminiWithSerializedTaxonomiesV1(onto)

    def classify_content(self, file):
        classification = {
            "Area": self.classifier.classify_area(file),
            "Ability": self.classifier.classify_ability(file),
            "Scope": self.classifier.classify_scope(file)
        }
        return classification
