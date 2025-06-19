import itertools
import sys
from pathlib import Path
from enum import IntEnum
from random import Random
from typing import Tuple, List, Dict

p = Path().absolute() / '../..'
sys.path.append(p.resolve().as_posix())

Random().seed(12345670)

from common import *
from ontology_populator.implementations.core import Implementation, Component, CopyTransformation, Transformation


def generate_main_tasks(graph: Graph) -> List[URIRef]:
    graph.add((cb.MainTask, RDF.type, tb.Task))
    graph.add((cb.DataProcessingTask, RDF.type, tb.Task))
    return [cb.MainTask, cb.DataProcessingTask]


def generate_algorithms(graph: Graph, tasks: List[URIRef]) -> List[URIRef]:
    algorithms = []
    for t in tasks:
        a = t.fragment.replace('Task', 'Algorithm')
        algorithms.append(cb[a])
        graph.add((cb[a], RDF.type, tb.Algorithm))
        graph.add((cb[a], tb.solves, t))
    return algorithms

def generate_datatag_base(graph:Graph):
    graph.add((dmop['TabularDataset'], RDFS.subClassOf, tb['Dataset']))
    # Base Shape
    graph.add((cb['TabularDataset'], RDF.type, tb.DataTag))
    graph.add((cb['TabularDataset'], RDF.type, SH.NodeShape))
    graph.add((cb['TabularDataset'], SH.targetClass, dmop.TabularDataset))

    return graph


datatag_id = 0
def create_datatag(graph:Graph):
    global datatag_id
    datatag = cb[f'Constraint_{datatag_id}']
    edge = cb[f'constraint_{datatag_id}']

    # Tag
    graph.add((datatag, RDF.type, tb.DataTag))
    graph.add((datatag, RDF.type, SH.NodeShape))
    graph.add((datatag, SH.targetClass, dmop.TabularDataset))
    graph.add((datatag, SH.property, cb[f'has_constraint_{datatag_id}']))

    # Constraint
    graph.add((cb[f'has_constraint_{datatag_id}'], RDF.type, SH.PropertyConstraintComponent))
    graph.add((cb[f'has_constraint_{datatag_id}'], SH.path, edge))
    graph.add((cb[f'has_constraint_{datatag_id}'], SH.datatype, XSD.boolean))
    graph.add((cb[f'has_constraint_{datatag_id}'], SH.hasValue, Literal(True)))

    datatag_id += 1

    return datatag, edge



# def generate_datatags(graph: Graph, num_constraints: int) -> Tuple[URIRef, List[Tuple[URIRef, URIRef]]]:

#     graph.add((dmop['TabularDataset'], RDFS.subClassOf, tb['Dataset']))
#     # Base Shape
#     graph.add((cb['TabularDataset'], RDF.type, tb.DataTag))
#     graph.add((cb['TabularDataset'], RDF.type, SH.NodeShape))
#     graph.add((cb['TabularDataset'], SH.targetClass, dmop.TabularDataset))

#     datatags = []
#     edge_dict = {}
#     for i in range(num_constraints):
#         datatag = cb[f'Constraint_{i}']
#         datatags.append(datatag)
#         edge_dict[datatag] = cb[f'constraint_{i}']

#         # Tag
#         graph.add((datatag, RDF.type, tb.DataTag))
#         graph.add((datatag, RDF.type, SH.NodeShape))
#         graph.add((datatag, SH.targetClass, dmop.TabularDataset))
#         graph.add((datatag, SH.property, cb[f'has_constraint_{i}']))

#         # Constraint
#         graph.add((cb[f'has_constraint_{i}'], RDF.type, SH.PropertyConstraintComponent))
#         graph.add((cb[f'has_constraint_{i}'], SH.path, cb[f'constraint_{i}']))
#         graph.add((cb[f'has_constraint_{i}'], SH.datatype, XSD.boolean))
#         graph.add((cb[f'has_constraint_{i}'], SH.hasValue, Literal(True)))
    
#     #Shape of the main component output
#     main_datatag = cb[f'Main_Output']
#     edge_dict[main_datatag] = cb[f'is_final_shape']
    
#     graph.add((main_datatag, RDF.type, tb.DataTag))
#     graph.add((main_datatag, RDF.type, SH.NodeShape))
#     graph.add((main_datatag, SH.targetClass, dmop.TabularDataset))
#     graph.add((main_datatag, SH.property, cb[f'is_final_shape']))


#     return cb['TabularDataset'], datatags, main_datatag, edge_dict


class RandomMethod(IntEnum):
    max = 0
    uniform = 1
    quadratic = 2


def get_random_up_to(components_per_requirement: int, method: RandomMethod = RandomMethod.quadratic) -> int:
    if method == RandomMethod.max:
        values = [components_per_requirement]
    elif method == RandomMethod.uniform:
        values = [i + 1 for i in range(components_per_requirement)]
    else:
        values = [i + 1 for i in range(components_per_requirement) for _ in range(2 ** i)]
    return Random().choice(values)


def create_implementation(implementation_name, inputs, outputs, type=cb.MainAlgorithm) -> Implementation:
    implementation = Implementation(implementation_name, type,
                                        [], [inputs], outputs, namespace=cb)
    return implementation


def create_component(component_name, implementation:Implementation, edges) -> Component:

    transformations = []
    for edge in edges:
        transformations.append(f"$output1 {edge.n3()} true .")
    transformations_str = "\n    ".join(transformations)

    component = Component(component_name, implementation, [
                CopyTransformation(1, 1),
                Transformation(
                    query=f'''
INSERT DATA {{
    {transformations_str}
}}
''',
                ),
            ], namespace=cb)
    
    return component



def generate_components(graph: Graph, num_main_impl:int, prep_depth:int, num_shapes_per_impl:int,
                              components_per_impl:int, implementations_per_shape:int, method: RandomMethod = RandomMethod.quadratic):
    
    input_shapes = []
    edg_dict = {}
    for i in range(max(2*num_main_impl, num_shapes_per_impl + 2)):
        inp, ed = create_datatag(graph)
        input_shapes.append(inp)
        edg_dict[inp] = ed

    num_shapes = get_random_up_to(num_shapes_per_impl, method)
    output_shape, edge_o_shape = create_datatag(graph)
    #Generate main components
    for i in range(num_main_impl):
        ish_impl = Random().sample([x for x in input_shapes], num_shapes)
        implementation = create_implementation(f'Main_Implementation_{i}',ish_impl,[output_shape])
        implementation.add_to_graph(graph)

        for j in range(components_per_impl):
            component = create_component(f'Main_Component_{i}_{j}',implementation,[edge_o_shape])
            component.add_to_graph(graph)

    MAX_PREPROCESSING_LEVEL = prep_depth
    level = 0

    while level <= MAX_PREPROCESSING_LEVEL:

        output_shapes = input_shapes
        input_shapes = []
        num_output_shapes = len(output_shapes)

        for i in range(num_output_shapes):
            inp, ed = create_datatag(graph)
            input_shapes.append(inp)
            edg_dict[inp] = ed

        num_prep_impl = implementations_per_shape*num_output_shapes

        for o_index in range(num_prep_impl): #create num_shapes_impl implementation per shape
            out = output_shapes[o_index % num_output_shapes]
            ish_impl = Random().sample([x for x in input_shapes], num_shapes)
            implementation = create_implementation(f'Prep_{level}_Implementation_{o_index}',ish_impl,[out],type=cb.DataProcessingAlgorithm)
            implementation.add_to_graph(graph)

            for j in range(components_per_impl):
                component = create_component(f'Prep_{level}_Component_{o_index}_{j}',implementation,[edg_dict[out]])
                component.add_to_graph(graph)
        
        level += 1
            

    #Ensure that each shape have a perfect implementation to solve it
    for input_shape in input_shapes:
        implementation = create_implementation(f'Base_Implementation_{input_shape.fragment}',[cb['TabularDataset']], [input_shape], type=cb.DataProcessingAlgorithm)
        implementation.add_to_graph(graph)
        component = create_component(f'Base_Component_{input_shape.fragment}',implementation, [edg_dict[input_shape]])
        component.add_to_graph(graph)
    
    # #Generate preprocessing components
    # for i in range(num_prep_impl):
    #     num_shapes = get_random_up_to(num_shapes_per_impl, method)
    #     input_shapes = Random().sample([x for x in datatags], num_shapes)
    #     output_shapes = Random().sample([x for x in datatags if x not in input_shapes], k=1) #output shapes should not match input shapes
    #     output_edges = [edge_dict[x] for x in output_shapes]
    #     print(input_shapes)
    #     print(output_shapes)
    #     implementation = create_implementation(f'Prep_Implementation_{i}',input_shapes, output_shapes, type=cb.DataProcessingAlgorithm)
    #     implementation.add_to_graph(graph)

    #     for j in range(components_per_impl):
    #         component = create_component(f'Prep_Component_{i}_{j}',implementation, output_edges)
    #         component.add_to_graph(graph)




def generate_fake_abox(num_main_implementations: int, prep_depth: int, num_components_per_implementation: int,
                       num_io_shapes_per_implementation:int, implementations_per_shape:int, folder: str):
    assert num_main_implementations > 0
    assert prep_depth >= 0
    assert num_components_per_implementation > 0
    assert num_io_shapes_per_implementation > 0

    cbox = get_graph_xp()
    tasks = generate_main_tasks(cbox)
    algorithms = generate_algorithms(cbox, tasks)
    #base_shape, datatags, main_output_shape, edge_dict = generate_datatags(cbox, num_constraints=max(2,num_prep_implementations // 2))
    generate_datatag_base(cbox)
    #transformations = generate_transformations(cbox, datatags, num_components_per_requirement, RandomMethod.max)
    #components = genereate_components(cbox, num_components, num_requirements_per_component, datatags,
    #                                  RandomMethod.max)

    generate_components(cbox, num_main_implementations, prep_depth, num_io_shapes_per_implementation, num_components_per_implementation,
                        implementations_per_shape, method=RandomMethod.max)

    file_name = f'cbox_{num_main_implementations}_{prep_depth}i_{num_io_shapes_per_implementation}shi_{implementations_per_shape}ish' \
                f'_{num_components_per_implementation}cpi.ttl'
    cbox.serialize(Path(folder)/file_name, format='turtle')


def generate_experiment_suite(folder: str):
    num_main_implementations = [ 1, 1, 1, 1, 1, 1 ]
    prep_depth = [ 1, 1, 1, 1, 1, 1]
    shapes_per_implementation = [2, 2, 2, 2, 2, 2]
    implementations_per_shape = [ 1, 1, 1, 1, 1, 1]
    num_components_per_implementation = [ 1, 2, 3, 4, 5, 6]

    for i in range(len(num_main_implementations)):
        generate_fake_abox(num_main_implementations[i], prep_depth[i], num_components_per_implementation[i], shapes_per_implementation[i], implementations_per_shape[i], folder)


if __name__ == '__main__':
    generate_experiment_suite('./fake_cboxes/generation_test')
