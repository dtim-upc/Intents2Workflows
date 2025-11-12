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

def get_implementation_parameters(ontology: Graph, implementation: URIRef, type:URIRef=tb.Parameter) -> Dict[
    URIRef, Tuple[Literal, Literal, Literal]]:
    parameters_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?parameter ?value ?order ?condition
        WHERE {{
            <{implementation}> tb:hasParameter ?parameter .
            ?parameter tb:has_defaultvalue ?value ;
                       a <{type}> .
            OPTIONAL {{ ?parameter tb:has_condition ?condition . }}
            OPTIONAL {{ ?parameter tb:has_position ?order . }}
        }}
        ORDER BY ?order
    """
    results = ontology.query(parameters_query).bindings
    return {param['parameter']: (param['value'], param.get('order',None), param.get('condition',None)) for param in results}


def get_text_parameter_base_parameter(ontology: Graph, factorParameter: URIRef):
    results = next(ontology.objects(factorParameter, tb.hasBaseParameter, unique=True),None)
    return results

def translate_factor_level(ontology:Graph, base_param:URIRef, base_level:str, engineParam:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?value
    WHERE {{
        {base_param.n3()} a tb:Parameter;
                tb:hasLevel ?baseFactor .
        ?baseFactor a tb:FactorLevel ;
                tb:hasValue "{base_level}" .
        {engineParam.n3()} tb:hasLevel ?engineFactor .
        ?engineFactor a tb:FactorLevel ;
            tb:equivalentTo ?baseFactor ;
            tb:hasValue ?value .
        
    }}
    '''
    result = ontology.query(query).bindings
    #print(query, result)
    return result[0]['value']

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

#Only used in run_generator
def get_component_exposed_parameters(ontology: Graph, component: URIRef) -> Dict[URIRef, Tuple[URIRef, Literal]]:
    expparams_query = f"""
    PREFIX tb: <{tb}>
    SELECT DISTINCT ?exp_param ?label ?value ?condition
    WHERE {{
        {task.n3()} a tb:Task .
        {{
            {"BIND(" + algorithm.n3() + " AS ?algorithm) ." if algorithm else f"?algorithm tb:solves {task.n3()} ."}
        }}
        # {'?algorithm' if algorithm is None else algorithm.n3()} tb:solves {task.n3()} .
        ?imp tb:implements ?algorithm .
        ?com tb:hasImplementation ?imp ;
            tb:exposesParameter ?exp_param .
        ?exp_param tb:has_defaultvalue ?value;
                tb:has_condition ?condition ;
                rdfs:label ?label .
    }}
    """
    
    result = ontology.query(expparams_query).bindings
    return result 

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


def get_engine(graph: Graph, implementation:URIRef):
    return next(graph.objects(implementation, tb.has_engine, unique=True),None)


def get_implementation_engine_compatibility(ontology:Graph, implementation: URIRef):
    return set(ontology.objects(implementation, tb.compatibleWith))

def is_predictor(ontology: Graph, implementation: URIRef):
    query = f""" PREFIX tb: <{tb}>
                ASK {{ {implementation.n3()} a tb:ApplierImplementation .}} """
    return ontology.query(query).askAnswer

def get_implementation_task(ontology: Graph, implementation: URIRef):
    query = f""" PREFIX tb: <{tb}>
                SELECT ?task
                WHERE {{ {implementation.n3()} tb:implements ?task .}} """
    
    results = ontology.query(query).bindings
    assert len(results) == 1

    return results[0]['task']


def get_parameter_datatype(ontology: Graph, parameter: URIRef):
    return next(ontology.objects(parameter, tb.has_datatype, True), None)


def get_algebraic_expression(ontology:Graph, param:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?expr
    WHERE {{
        {param.n3()} a tb:DerivedParameter;
                tb:derivedFrom ?expr .
        ?expr a tb:AlgebraicExpression .
                
    }}
    '''
    result = ontology.query(query).bindings
    return result[0]['expr'] 

def get_translation_condition(ontology: Graph, implementation:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?condition
    WHERE {{
        {implementation.n3()} tb:has_translation_condition ?condition .
        ?condition a tb:AlgebraicExpression .
                
    }}
    '''
    result = ontology.query(query).bindings
    if len(result) == 0:
        return None
    return result[0]['condition']

def get_engine_implementations(ontology: Graph, base_implementation:URIRef, engine:URIRef):

    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?impl
    WHERE {{
        ?impl a tb:EngineImplementation ;
            tb:has_engine {engine.n3()} ;
            tb:hasBaseImplementation {base_implementation.n3()} .          
    }}
    '''
    result = ontology.query(query).bindings
    
    return [r['impl'] for r in result]

def is_factor(ontology:Graph, parameter:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    ASK {{
        {parameter.n3()} a tb:FactorParameter .
    }}
    '''

    return ontology.query(query).askAnswer

def get_parameter_key(ontology:Graph, parameter:URIRef):
    return next(ontology.objects(parameter, tb.key, unique=True))

def is_shape_targeting_node(ontology:Graph, shape:URIRef, target_node:URIRef):
    query = f"""
    PREFIX tb: <{tb}>
    PREFIX sh: <{SH}>
    ASK {{ {shape.n3()} sh:targetClass ?class .
            ?class a { target_node.n3() } .
            }} 
    """
    return ontology.query(query).askAnswer

def is_shape_targeting_data(ontology:Graph, shape:URIRef):
    return is_shape_targeting_node(ontology, shape, tb.Dataset)

def is_shape_targeting_model(ontology:Graph, shape:URIRef):
    return is_shape_targeting_node(ontology, shape, tb.Model)