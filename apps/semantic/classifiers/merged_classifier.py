class MergedClassifier:

    def __init__(self, classifier):
        self.classifier = classifier

    def classify_content(self, file):
        classification = {
            "Area": self.classifier.classify_area(file),
            "Ability": self.classifier.classify_ability(file),
            "Scope": self.classifier.classify_scope(file)
        }
        return classification
