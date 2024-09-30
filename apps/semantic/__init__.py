import os
from dotenv import load_dotenv
from owlready2 import *

load_dotenv()

owlready2.JAVA_EXE = os.getenv("JAVA_RUNTIME")
sync_reasoner()

onto = get_ontology("./../core-ontology.rdf").load()
onto.base_iri = "http://edugraph.io/edu"