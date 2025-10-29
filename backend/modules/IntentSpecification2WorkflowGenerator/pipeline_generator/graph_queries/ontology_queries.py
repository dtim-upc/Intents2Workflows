from typing import Dict, List, Literal as Lit, Tuple
from rdflib import Graph, URIRef, Literal
from common import *


def get_implementation_input_specs(ontology: Graph, implementation: URIRef, maxImportanceLevel: int = 3):
    return get_implementation_io_specs(ontology, implementation, "Input", maxImportanceLevel)

def get_implementation_output_specs(ontology: Graph, implementation: URIRef, maxImportanceLevel: int = 3):
    return get_implementation_io_specs(ontology, implementation, "Output", maxImportanceLevel)

def get_implementation_io_specs(ontology: Graph, implementation: URIRef, type = Lit["Input", "Output"], maxImportanceLevel: int = 3) -> List[List[URIRef]]:
    
    assert type in ["Input", "Output"], f"invalid type {type}"
    
    input_spec_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?position ?spec (GROUP_CONCAT(?shape; SEPARATOR=",") AS ?shapes)
        WHERE {{
            {implementation.n3()} tb:specifies{type} ?spec .
            ?spec a tb:DataSpec ;
                tb:hasSpecTag ?sptg ;
                tb:has_position ?position .
            ?sptg 
                tb:hasImportanceLevel ?imp ;
                tb:hasDatatag ?shape . 
            FILTER(?imp <= {int(maxImportanceLevel)}) .

        }}
		GROUP BY ?position ?spec
        ORDER BY ?position
    """ #TODO check shape type datatag
    results = ontology.query(input_spec_query).bindings


    def unpack_shapes(shapes:str) -> List[URIRef]:
        spec_shapes = shapes.split(',')
        spec_shapes_uris = [URIRef(s) for s in spec_shapes]

        def shape_to_top(shape,uris):
            uris.remove(shape)
            uris.insert(0,shape)

        # Logical planner is only executed correctly if traintabular shape goes first. TODO Change this behaviour
        if cb.TrainTabularDatasetShape in spec_shapes_uris:
            shape_to_top(cb.TrainTabularDatasetShape, spec_shapes_uris)
        if cb.TestTabularDatasetShape in spec_shapes_uris:
            shape_to_top(cb.TestTabularDatasetShape, spec_shapes_uris)
        if cb.TrainTensorDatasetShape in spec_shapes_uris:
            shape_to_top(cb.TrainTensorDatasetShape, spec_shapes_uris)
        if cb.TestTensorDatasetShape in spec_shapes_uris:
            shape_to_top(cb.TestTensorDatasetShape, spec_shapes_uris)
        return spec_shapes_uris
    

    if results == [{}]:
        return []
    shapes = [(result['spec'],unpack_shapes(result['shapes'])) for result in results]
    return shapes



def find_implementations_to_satisfy_shape(ontology: Graph, shape: URIRef, exclude_appliers: bool = False) -> List[URIRef]:
    implementation_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?implementation
        WHERE {{
            {{
                ?implementation a tb:Implementation;
                                tb:specifiesOutput ?spec .
            }}
            FILTER NOT EXISTS {{
                ?implementation a tb:{'Applier' if exclude_appliers else ''}Implementation .
                                # tb:specifiesOutput ?spec .
            }}
            ?spec tb:hasSpecTag ?sptg .
            ?sptg tb:hasDatatag {shape.n3()} .
            FILTER NOT EXISTS {{
                ?implementation  tb:specifiesInput ?inpspec .
                ?inpspec tb:hasSpecTag ?inpsptg .
                ?inpsptg tb:hasDatatag {shape.n3()} .

            }}
        }}
    """
    result = ontology.query(implementation_query).bindings
    implementations = [x['implementation'] for x in result]

    return implementations


def get_implementation_components(ontology: Graph, implementation: URIRef) -> List[URIRef]:
    components_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?component
        WHERE {{
            ?component tb:hasImplementation {implementation.n3()} .
        }}
    """
    results = ontology.query(components_query).bindings
    return [result['component'] for result in results]


def retreive_component_rules(graph: Graph, task:URIRef, component: URIRef):
    preference_query = f"""
        PREFIX rdfs: <{RDFS}>

        SELECT ?datatag ?weight ?component_rank
        WHERE {{
            {component.n3()} tb:hasRule ?rule .
            ?rule tb:relatedtoDatatag ?datatag ;
                  tb:relatedtoTask {task.n3()} ;
                  tb:has_rank ?component_rank .
            ?datatag tb:has_weight ?weight .
        }}
    """
    results = graph.query(preference_query).bindings

    return {result['datatag']: (float(result['weight']), int(result['component_rank'])) for result in results}

def get_applier(ontology: Graph, component: URIRef):
    return next(ontology.objects(component, tb.hasApplier, True), None)


def get_algorithms_from_task(ontology: Graph, task: URIRef) -> URIRef:

    algorithm_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT DISTINCT ?algorithm
    WHERE{{
        ?algorithm a tb:Algorithm ;
                   tb:solves {task.n3()} .
        ?impl tb:implements ?algorithm .
        FILTER NOT EXISTS{{
            ?algorithm a tb:Algorithm ;
                   tb:solves {task.n3()} .
            ?impl a tb:ApplierImplementation.
        }}
    }}
"""
    result = ontology.query(algorithm_task_query).bindings
    algos = [algo['algorithm'] for algo in result]
    return algos


def get_potential_implementations(ontology: Graph, algorithm: URIRef, exclude_appliers=True) -> \
        List[URIRef]:
    main_implementation_query = f"""
    PREFIX tb: <{tb}>
    SELECT DISTINCT ?implementation
    WHERE {{
        ?implementation a tb:Implementation ;
            tb:implements {algorithm.n3()} .
        {algorithm.n3()} a tb:Algorithm ;
        { "FILTER NOT EXISTS {?implementation a tb:ApplierImplementation . }" if exclude_appliers else ''}
    }}
"""
    results = ontology.query(main_implementation_query).bindings
    implementations = [result['implementation'] for result in results]

    return implementations
                    
def get_constraint_by_name(ontology:Graph, constraint_name:str):
    query = f"""
    PREFIX tb: <{tb}>
    SELECT ?constraint
    WHERE {{
        ?constraint a tb:ExperimentConstraint ;
        rdfs:label "{constraint_name}" .
    }}
    """

    result = ontology.query(query).bindings

    if len(result) == 1:
        return result[0]["constraint"]
    
    return None

def get_engines(ontology: Graph):
    return set(ontology.subjects(RDF.type, tb.Engine)) # Repetitions here make no sense, so using set


def get_component_implementation(ontology: Graph, component: URIRef) -> URIRef:
    implementation_query = f"""
        PREFIX tb: <{tb}>
        PREFIX cb: <{cb}>
        SELECT ?implementation
        WHERE {{
            {component.n3()} tb:hasImplementation ?implementation .
        }}
    """
    result = ontology.query(implementation_query).bindings
    assert len(result) == 1
    return result[0]['implementation']

def get_implementation_parameters(ontology: Graph, implementation: URIRef) -> Dict[
    URIRef, Tuple[Literal, Literal, Literal]]:
    parameters_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?parameter ?value ?order ?condition
        WHERE {{
            <{implementation}> tb:hasParameter ?parameter .
            ?parameter tb:has_defaultvalue ?value ;
                       tb:has_condition ?condition ;
                       tb:has_position ?order .
        }}
        ORDER BY ?order
    """
    results = ontology.query(parameters_query).bindings
    return {param['parameter']: (param['value'], param['order'], param['condition']) for param in results}


def get_component_overridden_parameters(ontology: Graph, component: URIRef) -> Dict[URIRef, Tuple[URIRef, Literal]]:
    paramspecs_query = f"""
        PREFIX tb:<{tb}>
        SELECT ?parameterSpec ?parameter ?parameterValue ?position
        WHERE{{
            {component.n3()} tb:overridesParameter ?parameterSpec .
            ?parameterSpec tb:hasValue ?parameterValue .
            ?parameter tb:specifiedBy ?parameterSpec ;
                       tb:has_position ?position .
        }}
    """
    results = ontology.query(paramspecs_query).bindings
    overridden_params = {paramspec['parameter']: (paramspec['parameterValue'], paramspec['position'], None) for paramspec in results}

    return overridden_params


def get_component_transformations(ontology: Graph, component: URIRef) -> List[URIRef]:
    transformation_query = f'''
        PREFIX tb: <{tb}>
        SELECT ?transformation
        WHERE {{
            <{component}> tb:hasTransformation ?transformation_list .
            ?transformation_list rdf:rest*/rdf:first ?transformation .
        }}
    '''
    transformations = ontology.query(transformation_query).bindings
    return [x['transformation'] for x in transformations]