from owlready2 import *


onto = get_ontology("./../core-ontology.rdf").load()
onto.base_iri = "http://edugraph.io/edu"