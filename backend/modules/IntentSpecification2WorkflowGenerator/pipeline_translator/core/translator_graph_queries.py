import os
from typing import Dict, List, Tuple
import sys

import rdflib

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common import *
from pipeline_generator.graph_queries import get_implementation_io_specs
from .algebraic_expression_computation import compute_algebraic_expression

def get_ontology() -> Graph:
    cwd = os.getcwd()
    os.chdir('..')
    ontology = common.get_ontology_graph()
    os.chdir(cwd)
    return ontology
    

def get_input_specs(ontology, implementation):
    return get_implementation_io_specs(ontology, implementation, "Input")


def is_predictior(ontology: Graph, implementation: URIRef):
    query = f""" PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                ASK {{ {implementation.n3()} a tb:ApplierImplementation .}} """
    return ontology.query(query).askAnswer
   

def get_implementation_task(ontology: Graph, implementation: URIRef):
    query = f""" PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?task
                WHERE {{ {implementation.n3()} tb:implements ?task .}} """
    
    
    results = ontology.query(query).bindings

    assert len(results) == 1

    return results[0]['task']


def load_workflow(path: str) -> Graph:
    graph = get_graph_xp()
    graph.parse(path, format='turtle')
    return graph


def get_workflow_steps(graph: Graph) -> List[URIRef]:
    steps = list(graph.subjects(RDF.type, tb.Step))

    connections = list(graph.subject_objects(tb.followedBy))
    disordered = True
    while disordered:
        disordered = False
        for source, target in connections:
            si = steps.index(source)
            ti = steps.index(target)
            if si > ti:
                disordered = True
                steps[si] = target
                steps[ti] = source
    return steps


def get_step_component_implementation(ontology: Graph, workflow_graph: Graph, step: URIRef) -> Tuple[URIRef, URIRef]:
    component = next(workflow_graph.objects(step, tb.runs, True))
    implementation = next(ontology.objects(component, tb.hasImplementation, True))
    return component, implementation

def get_step_parameters(ontology: Graph, workflow_graph: Graph, step: URIRef) -> List[Tuple[str, str, str, URIRef]]:
    # print(f'STEP: {step}')
    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))
    # print(f'PARAMETERS: {len(parameters)}')
    param_specs = [next(workflow_graph.objects(param, tb.specifiedBy, True)) for param in parameters]
    # print(f'PARAM SPECS: {param_specs}')
    param_values = [next(workflow_graph.objects(ps, tb.hasValue, True)) for ps in param_specs]
    # print(f'VALUES: {param_values}')
    keys = [next(ontology.objects(p, tb.knime_key, True), None) for p in parameters]
    # print(f'KEYS: {len(keys)}')
    paths = [next(ontology.objects(p, tb.knime_path, True)).value for p in parameters]
    # print(f'PATHS: {paths}')
    types = [next(ontology.objects(p, tb.has_datatype, True)) for p in parameters]
    # print(f'TYPES: {types}')
    return list(zip(keys, param_values, paths, types))

def get_parameter_datatype(ontology: Graph, parameter: URIRef):
    return next(ontology.objects(parameter, tb.has_datatype, True), None)

def get_step_io_specs(workflow_graph:Graph, step:URIRef, type:str):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?pos ?spec
                WHERE {{ 
                    {step.n3()} tb:has{type} ?inp .
                    ?inp tb:has_spec ?spec ;
                        tb:has_position ?pos .       
                }} 
                ORDER BY ?pos
            """
    results = workflow_graph.query(query).bindings
    return [result['spec'] for result in results]

def get_step_input_specs(workflow_graph:Graph, step:URIRef):
    return get_step_io_specs(workflow_graph, step, 'Input')

def get_step_output_specs(workflow_graph:Graph, step:URIRef):
    return get_step_io_specs(workflow_graph, step, 'Output')

def get_step_inputs(workflow_graph:Graph, step:URIRef):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?pos ?data 
                WHERE {{ 
                    {step.n3()} tb:hasInput ?inp .
                    ?inp 
                        tb:has_data ?data ;
                        tb:has_position ?pos .       
                }} 
                ORDER BY ?pos"""
    result = workflow_graph.query(query).bindings
    return [ inp['data'] for inp in result ]

def get_step_outputs(workflow_graph:Graph, step:URIRef):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?pos ?data 
                WHERE {{ 
                    {step.n3()} tb:hasOutput ?inp .
                    ?inp 
                        tb:has_data ?data ;
                        tb:has_position ?pos .      
                }} 
                ORDER BY ?pos"""
    result = workflow_graph.query(query).bindings
    return [ inp['data'] for inp in result ]

def is_applier_step(ontology: Graph, workflow_graph:Graph, step:URIRef):
    component = next(workflow_graph.objects(step, tb.runs,True))

    askquery = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                    ASK {{
                        {component.n3()} a tb:ApplierComponent
                    }}"""
    result = ontology.query(askquery).askAnswer
    
    return result

def get_data_path(workflow_graph:Graph, data:URIRef):
    return next(workflow_graph.objects(data,dmop.path,True),None)


def get_workflow_intent_name(workflow_graph: Graph) -> str:
    return next(workflow_graph.subjects(RDF.type, tb.Intent, True)).fragment


def get_workflow_intent_number(workflow_graph: Graph) -> int:
    return int(next(workflow_graph.subjects(RDF.type, tb.Workflow, True)).fragment.split('_')[1])

def get_workflow_connections(workflow_graph: Graph) -> List[Tuple[URIRef, URIRef, URIRef, URIRef]]:
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?source ?destination ?sourcePort ?destinationPort
    WHERE {{
        ?source a tb:Step ;
                tb:followedBy ?destination ;
                tb:hasOutput ?output .
        ?output tb:has_position ?sourcePort ;
                tb:has_data ?link .
        ?destination a tb:Step ;
                    tb:hasInput ?input .
        ?input tb:has_position ?destinationPort ;
                tb:has_data ?link .
    }}
    '''
    results = workflow_graph.query(query).bindings
    # print(f'RESULTS: {results}')
    return [(r['source'], r['destination'], r['sourcePort'], r['destinationPort']) for r in results]


def get_text_params(ontology:Graph, implementation:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?param
    WHERE {{
        {implementation.n3()} a tb:Implementation ;
                tb:hasParameter ?param .
        ?param a tb:TextParameter .
                
    }}
    '''
    results = ontology.query(query).bindings
    return [r['param'] for r in results]

def get_engine_specific_params(ontology:Graph, implementation:URIRef): #TODO: merge with get_engine_specific_params with get_text_params and get_numerc_params
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?param
    WHERE {{
        {implementation.n3()} a tb:Implementation ;
                tb:hasParameter ?param .
        ?param a tb:EngineSpecificParameter .
                
    }}
    '''
    results = ontology.query(query).bindings
    return [r['param'] for r in results]

def is_factor(ontology:Graph, parameter:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    ASK {{
        {parameter.n3()} a tb:FactorParameter .
    }}
    '''

    return ontology.query(query).askAnswer


def get_numeric_params(ontology: Graph, implementation: URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?param
    WHERE {{
        {implementation.n3()} a tb:Implementation ;
                tb:hasParameter ?param .
        ?param a tb:NumericParameter .
                
    }}
    '''
    results = ontology.query(query).bindings
    return [r['param'] for r in results]

def get_base_param(ontology: Graph, factorParameter: URIRef):
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

def get_default_value(ontology: Graph, parameter:URIRef):
    return next(ontology.objects(parameter,tb.has_default_value),None)

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

def get_engine_implementation(ontology: Graph, base_implementation:URIRef, parameters:dict, engine:URIRef):
    print(engine)
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
    
    if len(result) > 1:
        for r in result:
            implementation = r['impl']
            cond = get_translation_condition(ontology, implementation)
            print("Condition:", cond, "parameters:", parameters, implementation)
            #print(compute_algebraic_expression(ontology, cond, parameters))
            if compute_algebraic_expression(ontology, cond, parameters):
                return implementation
        print(f"ERROR: No translation condition matched for {base_implementation} in {engine} engine.")
        return None
        #print(f"WARNING: More than one engine implementations found for {base_implementation} in {engine} engine. Only one of them (chosen randomly) will be used")
    elif len(result) <= 0:
        return None
    
    return result[0]['impl'] 

def get_engine_parameter(ontology: Graph, key: str, implementation:URIRef):
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?param
    WHERE {{
        ?param a tb:EngineParameter ;
            tb:key "{key}" .
        {implementation.n3()} tb:hasParameter ?param .           
    }}
    '''
    result = ontology.query(query).bindings
    
    if len(result) > 1:
        print(f"WARNING: More than one parameter found for key {key}. Only one of them  will be used")
    elif len(result) <= 0:
        print(f"WARNING: No parameter found for key {key}.")
        return None
    
    return result[0]['param']

def get_step_parameters_agnostic(workflow_graph: Graph, step: URIRef) -> Dict[URIRef,Literal]:

    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))
 
    step_parameters = {}

    for param in parameters:
        spec = next(workflow_graph.objects(param, tb.specifiedBy, True))
        value = next(workflow_graph.objects(spec, tb.hasValue, True))
        step_parameters[param] = value

    return step_parameters