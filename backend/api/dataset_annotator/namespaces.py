from rdflib import *

dmop = Namespace('http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#')
ab = Namespace('https://extremexp.eu/ontology/abox#')

def get_annotator_base_graph():
    g = Graph()
    g.bind('ab', ab)
    g.bind('dmop', dmop)
    return g