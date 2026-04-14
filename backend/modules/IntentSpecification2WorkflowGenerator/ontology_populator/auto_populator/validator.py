from rdflib import Graph, Namespace
import sys, os

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)


from common import sh as SH


shacl_graph = Graph()
shacl_graph.parse("../ontologies/cbox_deep.ttl", format="turtle")  # your SHACL graph

# Loop through all PropertyShapes
for shape in shacl_graph.subjects(predicate=None, object=None):
    # Check if this shape is a PropertyShape
    if (shape, None, SH.PropertyShape) in shacl_graph or (shape, None, SH.path) in shacl_graph:
        # Check if sh:path exists
        shapes = list(shacl_graph.objects(shape, SH.path))
        if not shapes:
            print("⚠ Shape missing sh:path (will fail in pySHACL):", shape)
    
for p in shacl_graph.objects(subject=None, predicate=SH.property):
    if (p, None, SH.PropertyShape) not in shacl_graph:
        print("Missing definition for", p)
