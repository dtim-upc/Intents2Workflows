from rdflib import Graph, Namespace
SH = Namespace("http://www.w3.org/ns/shacl#")

shacl_graph = Graph()
shacl_graph.parse("Ontology/cbox_gpt.ttl", format="turtle")  # your SHACL graph

# Loop through all PropertyShapes
for shape in shacl_graph.subjects(predicate=None, object=None):
    # Check if this shape is a PropertyShape
    if (shape, None, SH.PropertyShape) in shacl_graph or (shape, None, SH.path) in shacl_graph:
        # Check if sh:path exists
        if not list(shacl_graph.objects(shape, SH.path)):
            print("⚠ Shape missing sh:path (will fail in pySHACL):", shape)