from owlready2 import get_ontology

BASE_IRI = "http://edugraph.io/edu#"

class OntologyLoader:

    @staticmethod
    def load_from_path(path):
        onto = get_ontology(path).load()
        onto.base_iri = BASE_IRI
        return onto
