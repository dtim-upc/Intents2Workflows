import itertools
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Tuple, Any, List, Dict, Optional, Union, Set, Type
import random
import math
import ast

from pyshacl import validate
from tqdm import tqdm
from urllib.parse import quote

sys.path.append(os.path.join(os.path.abspath(os.path.join('..'))))
from common import *
from ontology_populator.implementations.core import *
from ontology_populator.implementations.knime.knime_implementation import KnimeParameter

def get_intent_iri(intent_graph: Graph) -> URIRef:
    intent_iri_query = f"""
PREFIX tb: <{tb}>
SELECT ?iri
WHERE {{
    ?iri a tb:Intent .
}}
"""
    result = intent_graph.query(intent_iri_query).bindings
    assert len(result) == 1
    return result[0]['iri']


def get_intent_dataset_task(intent_graph: Graph, intent_iri: URIRef) -> Tuple[URIRef, URIRef, URIRef]:
    dataset_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT ?dataset ?task ?algorithm
    WHERE {{
        {intent_iri.n3()} a tb:Intent .
        {intent_iri.n3()} tb:overData ?dataset .
        ?task tb:tackles {intent_iri.n3()} .
        OPTIONAL {{{intent_iri.n3()} tb:specifies ?algorithm}}
    }}
"""
    result = intent_graph.query(dataset_task_query).bindings[0]
    return result['dataset'], result['task'], result.get('algorithm', None)


def get_intent_parameters(intent_graph: Graph):
    intent_parameters_query = f"""
    PREFIX tb:<{tb}>
    SELECT ?exp_param ?param_val
    WHERE{{
        ?param_val tb:forParameter ?exp_param .
    }}
"""
    result = intent_graph.query(intent_parameters_query).bindings
    return {param['exp_param']:param['param_val'] for param in result}


def get_algorithms_from_task(ontology: Graph, task: URIRef) -> URIRef:

    algorithm_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT ?algorithm
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

def reinforce_constraint(ontology:Graph, shape_graph:Graph, node_shape:URIRef, unconstrained_nodes:List[URIRef]):
    constrained_nodes = []

    for node in unconstrained_nodes:
        if satisfies_shape(ontology, shape_graph, shape=node_shape, focus=node):
            constrained_nodes.append(node)
    
    return constrained_nodes

def get_algorithms_from_task_constrained(ontology:Graph, shape_graph:Graph, task: URIRef) -> URIRef:
    algs_unconstr = get_algorithms_from_task(ontology, task)
    return reinforce_constraint(ontology, shape_graph, ab.AlgorithmConstraint, algs_unconstr)


def get_exposed_parameters(ontology: Graph, task: URIRef, algorithm: URIRef):

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


def get_intent_info(intent_graph: Graph, intent_iri: Optional[URIRef] = None) -> \
        Tuple[URIRef, URIRef, List[Dict[str, Any]], URIRef]:
    if not intent_iri:
        intent_iri = get_intent_iri(intent_graph)

    dataset, task, algorithm = get_intent_dataset_task(intent_graph, intent_iri) 

    return dataset, task, algorithm, intent_iri 

def get_implementation_input_specs(ontology: Graph, implementation: URIRef, maxImportanceLevel: int = 3) -> List[List[URIRef]]:
    input_spec_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?spec (GROUP_CONCAT(?shape; SEPARATOR=",") AS ?shapes)
        WHERE {{
            {implementation.n3()} tb:specifiesInput ?spec .
            ?spec a tb:DataSpec ;
                tb:hasSpecTag ?sptg ;
                tb:has_position ?position .
            ?sptg 
                tb:hasImportanceLevel ?imp ;
                tb:hasDatatag ?shape . 
            FILTER(?imp <= {int(maxImportanceLevel)}) .

        }}
		GROUP BY ?spec
        ORDER BY ?position
    """ #TODO check shape type datatag
    results = ontology.query(input_spec_query).bindings

    if results == [{}]:
        return []
    shapes = [unpack_shapes(result['shapes']) for result in results]
    return shapes


def get_implementation_output_specs(ontology: Graph, implementation: URIRef) -> List[List[URIRef]]:
    output_spec_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?spec (GROUP_CONCAT(?shape; SEPARATOR=",") AS ?shapes)
        WHERE {{
            {implementation.n3()} tb:specifiesOutput ?spec .
            ?spec a tb:DataSpec ;
                tb:hasSpecTag ?sptg ;
                tb:has_position ?position .
            ?sptg tb:hasDatatag ?shape . 
        }}
		GROUP BY ?spec
        ORDER BY ?position
    """ #TODO check shap type datatagER BY ?position

    results = ontology.query(output_spec_query).bindings
    if results == [{}]:
        return []
    shapes = [unpack_shapes(result['shapes']) for result in results]
    return shapes

def unpack_shapes(shapes:str) -> List[URIRef]:
    spec_shapes = shapes.split(',')
    spec_shapes_uris = [URIRef(s) for s in spec_shapes]
    return spec_shapes_uris


# def get_all_implementations(ontology: Graph, task_iri: URIRef = None, algorithm: URIRef = None) -> \
#         List[Tuple[URIRef, List[URIRef]]]:
#     main_implementation_query = f"""
#     PREFIX tb: <{tb}>
#     SELECT DISTINCT ?implementation
#     WHERE {{
#         ?implementation a tb:Implementation ;
#             tb:implements {algorithm.n3() if algorithm is not None else '?algorithm'} .
#         ?algorithm a tb:Algorithm ;
#             tb:solves {task_iri.n3() if task_iri is not None else '?task'} .
#         ?subtask tb:subtaskOf* {task_iri.n3() if task_iri is not None else '?task'} .
#     }}
# """
#     results = ontology.query(main_implementation_query).bindings
#     implementations = [result['implementation'] for result in results]

#     implementations_with_shapes = [
#         (implementation, get_implementation_input_specs(ontology, implementation))
#         for implementation in implementations]

#     return implementations_with_shapes


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


def get_potential_implementations_constrained(ontology:Graph, shape_graph:Graph, algorithm: URIRef, exclude_appliers=True) -> \
        List[URIRef]:
    pot_impl_unconstr = get_potential_implementations(ontology, algorithm, exclude_appliers)
    return reinforce_constraint(ontology, shape_graph, ab.ImplementationConstraint, pot_impl_unconstr)


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

def get_implementation_components_constrained(ontology: Graph, shape_graph: Graph, implementation: URIRef) -> List[URIRef]:
    pot_comp_unconstr = get_implementation_components(ontology, implementation)
    return reinforce_constraint(ontology, shape_graph, ab.ComponentConstraint, pot_comp_unconstr)


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
        }}
    """
    result = ontology.query(implementation_query).bindings
    implementations = [x['implementation'] for x in result]

    return implementations

def find_implementations_to_satisfy_shape_constrained(ontology: Graph, shape_graph:Graph, shape: URIRef, exclude_appliers: bool = False) -> List[URIRef]:
    pot_impl_unconstr = find_implementations_to_satisfy_shape(ontology,shape,exclude_appliers)
    return reinforce_constraint(ontology,shape_graph,ab.ImplementationConstraint,pot_impl_unconstr)

def identify_data_io(ontology: Graph, ios: List[List[URIRef]], train: bool = False, test: bool = False, return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, io_shapes in enumerate(ios):
        for io_shape in io_shapes:
            if ((io_shape, SH.targetClass, dmop.TabularDataset) in ontology 
                or (io_shape, SH.targetClass, cb.TabularDatasetShape) in ontology 
                or io_shape.fragment == "TabularDatasetShape"):

                if test:
                    test_query = f'''
                    PREFIX sh: <{SH}>
                    PREFIX rdfs: <{RDFS}>
                    PREFIX cb: <{cb}>
                    PREFIX dmop: <{dmop}>

                    ASK {{
                        {{
                        {io_shape.n3()} a sh:NodeShape ;
                                        sh:targetClass dmop:TabularDataset ;
                                        sh:property [
                                            sh:path dmop:isTestDataset ;
                                            sh:hasValue true
                                        ] .
                        }}
                    }}
                    '''
                    result = ontology.query(test_query).askAnswer
                    if result:
                        return i if return_index else io_shapes
                    
                if train:
                    train_query = f'''
                    PREFIX sh: <{SH}>
                    PREFIX rdfs: <{RDFS}>
                    PREFIX cb: <{cb}>
                    PREFIX dmop: <{dmop}>

                    ASK {{
                        {{
                        {io_shape.n3()} a sh:NodeShape ;
                                        sh:targetClass dmop:TabularDataset ;
                                        sh:property [
                                            sh:path dmop:isTrainDataset ;
                                            sh:hasValue true
                                        ] .
                        }}
                    }}
                    '''
                    result = ontology.query(train_query).askAnswer
                    if result:
                        return i if return_index else io_shapes
                
                if not train and not test:
                    return i if return_index else io_shapes
            
def identify_model_io(ontology: Graph, ios: List[List[URIRef]], return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, io_shapes in enumerate(ios):
        for io_shape in io_shapes:
            query = f'''
    PREFIX sh: <{SH}>
    PREFIX rdfs: <{RDFS}>
    PREFIX cb: <{cb}>

    ASK {{
      {{
        {io_shape.n3()} sh:targetClass ?targetClass .
        ?targetClass rdfs:subClassOf* cb:Model .
      }}
      UNION
      {{
        {io_shape.n3()} rdfs:subClassOf* cb:Model .
      }}
    }}
'''
            if ontology.query(query).askAnswer:
                return i if return_index else io_shapes

def identify_visual_io(ontology: Graph, ios: List[List[URIRef]], return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, io_shapes in enumerate(ios):
        for io_shape in io_shapes:
            query = f'''
    PREFIX sh: <{SH}>
    PREFIX rdfs: <{RDFS}>
    PREFIX cb: <{cb}>

    ASK {{
      {{
        {io_shape.n3()} sh:targetClass ?targetClass .
        ?targetClass rdfs:subClassOf* cb:Visualization .
      }}
      UNION
      {{
        {io_shape.n3()} rdfs:subClassOf* cb:Visualization .
      }}
    }}
'''
            if ontology.query(query).askAnswer:
                return i if return_index else io_shapes

def satisfies_shape(data_graph: Graph, shacl_graph: Graph, shape: URIRef, focus: URIRef) -> bool:
    conforms, g, report = validate(data_graph, shacl_graph=shacl_graph, validate_shapes=[shape], focus=focus)

    #if not conforms:
    #    tqdm.write(report)

    return conforms

def get_shape_target_class(ontology: Graph, shape: URIRef) -> URIRef:
    return ontology.query(f"""
        PREFIX sh: <{SH}>
        SELECT ?targetClass
        WHERE {{
            <{shape}> sh:targetClass ?targetClass .
        }}
    """).bindings[0]['targetClass']


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


def get_component_non_overriden_parameters(ontology: Graph, component: URIRef) -> Dict[
    URIRef, Tuple[Literal, Literal, Literal]]:
    parameters_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?parameter ?parameterValue ?position ?condition
        WHERE {{
            {component.n3()} tb:hasImplementation ?implementation .
            ?implementation tb:hasParameter ?parameter .
            ?parameter tb:has_defaultvalue ?parameterValue ;
                       tb:has_position ?position ;
                       tb:has_condition ?condition .
            FILTER NOT EXISTS {{
                ?parameter tb:specifiedBy ?parameterSpecification .
            }}
        }}
        ORDER BY ?position
    """
    results = ontology.query(parameters_query).bindings
    return {param['parameter']: (param['parameterValue'], param['position'], param['condition']) for param in results}



def get_component_parameters(ontology: Graph, component: URIRef) -> Dict[URIRef, Tuple[Literal, Literal, Literal]]:
    component_params = get_component_non_overriden_parameters(ontology, component)
    return component_params



def get_component_overridden_paramspecs(ontology: Graph, workflow_graph: Graph, component: URIRef) -> Dict[URIRef, Tuple[URIRef, Literal]]:
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

    overridden_paramspecs = {paramspec['parameterSpec']: (paramspec['parameter'], paramspec['parameterValue'], paramspec['position']) for paramspec in results}

    for paramspec, paramval_tup in overridden_paramspecs.items():
        param, value, _ = paramval_tup
        workflow_graph.add((paramspec, RDF.type, tb.ParameterSpecification))
        workflow_graph.add((param, tb.specifiedBy, paramspec))
        workflow_graph.add((paramspec, tb.hasValue, value))

    return overridden_paramspecs



def perform_param_substitution(graph: Graph, implementation: URIRef, parameters: Dict[URIRef, Tuple[Literal, Literal, Literal]],
                               inputs: List[URIRef], intent_graph: Graph = None) -> Dict[URIRef, Tuple[Literal, Literal, Literal]]:
    
    parameter_keys = list(parameters.keys())
    intent_parameters = get_intent_parameters(intent_graph) if intent_graph is not None else {}
    intent_parameter_keys = list(intent_parameters.keys())

    #tqdm.write("intentParams")
    #tqdm.write(str(intent_parameters))

    updated_parameters = parameters.copy()

    for parameter, (default_value, position, condition) in parameters.items():
        if parameter in intent_parameter_keys:
            intent_value = intent_parameters[parameter]
            updated_parameters[parameter] = (intent_value, position, condition)
    
    #tqdm.write(str(parameters))
    #tqdm.write(str(updated_parameters))

    parameters.update(updated_parameters)
            

    for param in parameter_keys:
        value, order, condition = parameters[param]
        if condition.value is not None and condition.value != '':
            feature_types = get_inputs_feature_types(graph, inputs)
            if condition.value == '$$INTEGER_COLUMN$$' and int not in feature_types:
                parameters.pop(param)
                continue
            if condition.value == '$$STRING_COLUMN$$' and str not in feature_types:
                parameters.pop(param)
                continue
            if condition.value == '$$FLOAT_COLUMN$$' and float not in feature_types:
                parameters.pop(param)
                continue
        if isinstance(value.value, str) and '$$LABEL$$' in value.value:
            new_value = value.replace('$$LABEL$$', f'{get_inputs_label_name(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '$$LABEL_CATEGORICAL$$' in value.value: #this allows target column to be defined withou exposed parameters
            new_value = value.replace('$$LABEL_CATEGORICAL$$', f'{get_inputs_label_name(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '$$NUMERIC_COLUMNS$$' in value.value:
            new_value = value.replace('$$NUMERIC_COLUMNS$$', f'{get_inputs_numeric_columns(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '$$CSV_PATH$$' in value.value:
            new_value = value.replace('$$CSV_PATH$$', f'{get_csv_path(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '&amp;' in value.value:
            new_value = value.replace('&amp;', '&')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and value.value != '':
            if condition.value == '$$BAR_EXCLUDED$$':
                possible_cols = get_inputs_numeric_columns(graph, inputs)
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)
            elif condition.value == '$$HISTOGRAM_EXCLUDED$$':
                possible_cols = get_inputs_numeric_columns(graph, inputs)
                cat_col = [str(parameters[param][0]) for param in intent_parameters.keys() if 'histogram_category' in str(param)][0]
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(cat_col) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)
            elif condition.value == '$$HEATMAP_EXCLUDED$$':
                possible_cols = get_inputs_numeric_columns(graph, inputs)
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)
            elif condition.value == '$$LINEPLOT_EXCLUDED$$':
                possible_cols = get_inputs_all_columns(graph, inputs) + ['<RowID>']
                com_col = [str(parameters[param][0]) for param in intent_parameters.keys() if 'lineplot_x' in str(param)]
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(com_col) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)

    return parameters


def assign_to_parameter_specs(graph: Graph,
                              parameters: Dict[URIRef, Tuple[Literal, Literal, Literal]])-> Dict[URIRef, Tuple[URIRef, Literal]]:
    
    keys = list(parameters.keys())
    param_specs = {}
    
    for param in keys:

        value, order, _ = parameters[param]
        uri = param.split('#')[-1] if '#' in param else param.split('/')[-1]
        sanitized_value = quote(value, safe="-_")
        sanitized_uri = URIRef(f'{uri}_{sanitized_value}_specification'.replace(' ','_').lower())
        param_spec = ab.term(sanitized_uri)
        graph.add((param_spec, RDF.type, tb.ParameterSpecification))
        graph.add((param, tb.specifiedBy, param_spec))
        graph.add((param_spec, tb.hasValue, value))

        param_specs[param_spec] = (param, value, order)
    
    return param_specs


def add_step(graph: Graph, pipeline: URIRef, task_name: str, component: URIRef,
             parameter_specs: Dict[URIRef, Tuple[URIRef, Literal]],
             order: int, previous_task: Union[None, list, URIRef] = None, inputs: Optional[List[URIRef]] = None,
             outputs: Optional[List[URIRef]] = None) -> URIRef:
    if outputs is None:
        outputs = []
    if inputs is None:
        inputs = []
    step = ab.term(task_name)
    graph.add((pipeline, tb.hasStep, step))
    graph.add((step, RDF.type, tb.Step))
    graph.add((step, tb.runs, component))
    graph.add((step, tb.has_position, Literal(order)))
    for i, input in enumerate(inputs):
        in_node = BNode()
        graph.add((in_node, RDF.type, tb.Data))
        graph.add((in_node, tb.has_data, input))
        graph.add((in_node, tb.has_position, Literal(i)))
        graph.add((step, tb.hasInput, in_node))
    for o, output in enumerate(outputs):
        out_node = BNode()
        graph.add((out_node, RDF.type, tb.Data))
        graph.add((out_node, tb.has_data, output))
        graph.add((out_node, tb.has_position, Literal(o)))
        graph.add((step, tb.hasOutput, out_node))
    for param, *_ in parameter_specs.values():
        graph.add((step, tb.usesParameter, param))
    if previous_task:
        if isinstance(previous_task, list):
            for previous in previous_task:
                graph.add((previous, tb.followedBy, step))
        else:
            graph.add((previous_task, tb.followedBy, step))
    return step


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


def get_inputs_all_columns(graph: Graph, inputs: List[URIRef]) -> List:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
        }}
    """
    columns = graph.query(columns_query).bindings
    return [x['label'].value for x in columns]


def get_inputs_label_name(graph: Graph, inputs: List[URIRef]) -> str:
    
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)

    label_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isLabel true ;
                    dmop:hasColumnName ?label .

        }}
    """
    
    results = graph.query(label_query).bindings
    
    if results is not None and len(results) > 0:
        return results[0]['label']
    

def get_exact_column(graph: Graph, inputs: List[URIRef], column_name: str) -> str:
    
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)

    column_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:hasColumnName ?label .
            FILTER(?label = "{column_name}")
        }}
    """
    
    results = graph.query(column_query).bindings
    
    if results is not None and len(results) > 0:
        return results[0]['label']


def get_inputs_numeric_columns(graph: Graph, inputs: List[URIRef]) -> str:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
            FILTER(?type IN (dmop:Float, dmop:Int, dmop:Number, dmop:Double, dmop:Long, dmop:Short, dmop:Integer))
        }}
    """
    columns = graph.query(columns_query).bindings
 
    return [x['label'].value for x in columns]


def get_inputs_categorical_columns(graph: Graph, inputs: List[URIRef]) -> str:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)

    categ_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isCategorical true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
        }}
    """
    columns = graph.query(categ_query).bindings

    return [x['label'].value for x in columns]


def get_csv_path(graph: Graph, inputs: List[URIRef]) -> str:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    path = next(graph.objects(data_input, dmop.path), True)
    return path.value


def get_inputs_feature_types(graph: Graph, inputs: List[URIRef]) -> Set[Type]:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?type
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type .
        }}
    """
    columns = graph.query(columns_query).bindings
    mapping = {
        dmop.Float: float,
        dmop.Int: int,
        dmop.Integer: int,
        dmop.Number: float,
        dmop.Double: float,
        dmop.String: str,
        dmop.Boolean: bool,
    }
    return set([mapping[x['type']] for x in columns])


def copy_subgraph(source_graph: Graph, source_node: URIRef, destination_graph: Graph, destination_node: URIRef,
                  replace_nodes: bool = True) -> None:
    visited_nodes = set()
    nodes_to_visit = [source_node]
    mappings = {source_node: destination_node}

    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        visited_nodes.add(current_node)
        for predicate, object in source_graph.predicate_objects(current_node):
            if predicate == OWL.sameAs:
                continue
            if replace_nodes and isinstance(object, IdentifiedNode):
                if predicate == RDF.type or object in dmop:
                    mappings[object] = object
                else:
                    if object not in visited_nodes:
                        nodes_to_visit.append(object)
                    if object not in mappings:
                        mappings[object] = BNode()
                destination_graph.add((mappings[current_node], predicate, mappings[object]))
            else:
                destination_graph.add((mappings[current_node], predicate, object))


def annotate_io_with_spec(ontology: Graph, workflow_graph: Graph, io: URIRef, io_spec: List[URIRef]) -> None:
    
    for spec in io_spec:
        
        io_spec_class = next(ontology.objects(spec, SH.targetClass, True), None)

        if io_spec_class is None or (io, RDF.type, io_spec_class) in workflow_graph:
            continue

        workflow_graph.add((io, RDF.type, io_spec_class))


def annotate_ios_with_specs(ontology: Graph, workflow_graph: Graph, data_io: List[URIRef],
                            specs: List[List[URIRef]]) -> None:
    assert len(data_io) == len(specs), 'Number of IOs and specs must be the same'
    for io, spec in zip(data_io, specs):
        annotate_io_with_spec(ontology, workflow_graph, io, spec)


def run_copy_transformation(ontology: Graph, workflow_graph: Graph, transformation: URIRef, inputs: List[URIRef],
                            outputs: List[URIRef]):
    input_index = next(ontology.objects(transformation, tb.copy_input, True)).value
    output_index = next(ontology.objects(transformation, tb.copy_output, True)).value
    #tqdm.write(f"Copy transformation: i:{str(input_index)} o:{str(output_index)}")
    input = inputs[input_index - 1]
    output = outputs[output_index - 1]

    copy_subgraph(workflow_graph, input, workflow_graph, output)


def run_component_transformation(ontology: Graph, workflow_graph: Graph, component: URIRef, inputs: List[URIRef],
                                 outputs: List[URIRef],
                                 parameters_specs: Dict[URIRef, Tuple[URIRef, Literal, Literal]]) -> None:
    transformations = get_component_transformations(ontology, component)
    #tqdm.write("run_component_transformation")
    
    for transformation in transformations:
        #tqdm.write(str(transformation))
        if (transformation, RDF.type, tb.CopyTransformation) in ontology:
            run_copy_transformation(ontology, workflow_graph, transformation, inputs, outputs)
        elif (transformation, RDF.type, tb.LoaderTransformation) in ontology:
            #tqdm.write("loader_transformation")
            continue
        else:
            prefixes = f'''
PREFIX tb: <{tb}>
PREFIX ab: <{ab}>
PREFIX rdf: <{RDF}>
PREFIX rdfs: <{RDFS}>
PREFIX owl: <{OWL}>
PREFIX xsd: <{XSD}>
PREFIX dmop: <{dmop}>
'''
            query = next(ontology.objects(transformation, tb.transformation_query, True)).value
            query = prefixes + query
            for i in range(len(inputs)):
                query = query.replace(f'$input{i + 1}', f'{inputs[i].n3()}')
            for i in range(len(outputs)):
                query = query.replace(f'$output{i + 1}', f'{outputs[i].n3()}')
            for param_spec, (param, value, order) in parameters_specs.items():
                #tqdm.write(param_spec)
                #tqdm.write(param)
                #tqdm.write(value)
                #tqdm.write(order)
                query = query.replace(f'$param{order + 1}', f'{value.n3()}')
                query = query.replace(f'$parameter{order + 1}', f'{value.n3()}')
            
            #tqdm.write("Query:")
            #tqdm.write(str(query))
            workflow_graph.update(query)

            


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


def get_best_components(graph: Graph, task: URIRef, components: List[URIRef], dataset: URIRef, percentage: float = None):

    preferred_components = {}
    sorted_components = {}
    for component in components:
        
        component_rules = retreive_component_rules(graph, task, component)
        score = 0

        preferred_components[component] = score

        for datatag, weight_rank in component_rules.items():
            rule_weight = weight_rank[0]
            component_rank = weight_rank[1]
            if satisfies_shape(graph, graph, datatag, dataset):
                score+=rule_weight
            else:
                score-=rule_weight
                
            preferred_components[component] = (score, component_rank)
        
    sorted_preferred = sorted(preferred_components.items(), key=lambda x: x[1][0], reverse=True)

    if len(sorted_preferred) > 0: ### there are multiple components to choose from
        best_scores = set([comp[1] for comp in sorted_preferred])
        if len(best_scores) == 1:
            sorted_preferred = random.sample(sorted_preferred, int(math.ceil(len(sorted_preferred)*percentage))) if percentage else sorted_preferred
        elif len(best_scores) > 1: ### checking if there is at least one superior component
            sorted_preferred = [x for x in sorted_preferred if x[1] >= sorted_preferred[0][1]]


    for comp, rules_nbr in sorted_preferred:
        sorted_components[comp] = rules_nbr 

    return sorted_components


def prune_workflow_combinations(ontology:Graph, shape_graph:Graph, combinations: List[Tuple[int,URIRef]], main_component:URIRef) -> List[Tuple[int,URIRef]]:
        
        temporal_graph = ontology #WARNING: temporal_graph is just an alias. Ontology is modified.
        combinations_constrained = []
        for i, tc in combinations:
            workflow_name = f'workflow_{main_component.fragment}_{i}'
            workflow = tb.term(workflow_name)
            temporal_graph.add((workflow, RDF.type, tb.Workflow))
            
            triples_to_add = []
            triples_to_add.append((workflow, tb.hasComponent, main_component, temporal_graph))

            for component in tc:
                triples_to_add.append((workflow, tb.hasComponent, component, temporal_graph))  
            
            temporal_graph.addN(triples_to_add)

            if satisfies_shape(temporal_graph, shape_graph, shape=ab.WorkflowConstraint, focus=workflow):
                combinations_constrained.append(tc)
        return list(enumerate(combinations_constrained))

    


def get_step_name(workflow_name: str, task_order: int, implementation: URIRef) -> str:
    return f'{workflow_name}-step_{task_order}_{implementation.fragment.replace("-", "_")}'


def add_loader_step(ontology: Graph, workflow_graph: Graph, workflow: URIRef, dataset_node: URIRef) -> URIRef:
    loader_component = cb.term('component-csv_local_reader')
    loader_step_name = get_step_name(workflow.fragment, 0, loader_component)
    loader_parameters = get_component_parameters(ontology, loader_component)
    loader_overridden_paramspecs = get_component_overridden_paramspecs(ontology, workflow_graph, loader_component)
    loader_parameters = perform_param_substitution(workflow_graph, None, loader_parameters, [dataset_node])
    loader_param_specs = assign_to_parameter_specs(workflow_graph, loader_parameters)
    loader_param_specs.update(loader_overridden_paramspecs)
    return add_step(workflow_graph, workflow, loader_step_name, loader_component, loader_param_specs, 0, None, None,
                    [dataset_node])


def build_general_workflow(workflow_name: str, ontology: Graph, dataset: URIRef, main_component: URIRef,
                           transformations: List[URIRef], intent_graph:Graph) -> Tuple[Graph, URIRef]:
    
    tqdm.write("\n\n BUILDING WORKFLOW")

    workflow_graph = get_graph_xp()
    workflow = ab.term(workflow_name)
    workflow_graph.add((workflow, RDF.type, tb.Workflow))
    task_order = 0

    intent_iri = get_intent_iri(intent_graph)
    max_imp_level = int(next(intent_graph.objects(intent_iri, tb.has_complexity), None))

    dataset_node = ab.term(f'{workflow_name}-original_dataset')

    copy_subgraph(ontology, dataset, workflow_graph, dataset_node)

    loader_step = add_loader_step(ontology, workflow_graph, workflow, dataset_node)
    task_order += 1

    previous_step = loader_step
    previous_train_step = loader_step
    previous_test_step = None

    previous_node = dataset_node
    train_dataset_node = dataset_node
    test_dataset_node = None


    for train_component in [*transformations, main_component]:
        #tqdm.write("components")
        #tqdm.write(train_component)
    
        test_component = next(ontology.objects(train_component, tb.hasApplier, True), None)
        #if not test_component is None:
        #    tqdm.write(test_component)
        same = train_component == test_component
        train_component_implementation = get_component_implementation(ontology, train_component)


        if not test_component:
            
            singular_component = train_component
            singular_step_name = get_step_name(workflow_name, task_order, singular_component)
            singular_component_implementation = get_component_implementation(ontology, singular_component)
            singular_input_specs = get_implementation_input_specs(ontology, singular_component_implementation,max_imp_level)
            singular_input_data_index = identify_data_io(ontology, singular_input_specs, return_index=True)
            singular_transformation_inputs = None

            #tqdm.write("Sepecs singular input:")
            #tqdm.write(str(singular_input_specs))

            if singular_input_data_index is not None:
                singular_transformation_inputs = [ab[f'{singular_step_name}-input_{i}'] for i in range(len(singular_input_specs))]
                singular_transformation_inputs[singular_input_data_index] = previous_node
                #tqdm.write(str(singular_transformation_inputs))
                annotate_ios_with_specs(ontology, workflow_graph, singular_transformation_inputs,
                                        singular_input_specs)
            
            #tqdm.write("Singular output:")
            singular_output_specs = get_implementation_output_specs(ontology, singular_component_implementation)
            singular_transformation_outputs = [ab[f'{singular_step_name}-output_{i}'] for i in range(len(singular_output_specs))]
            annotate_ios_with_specs(ontology, workflow_graph, singular_transformation_outputs,
                                singular_output_specs)
            
            #tqdm.write("Sepecs singular output:")
            #tqdm.write(str(singular_output_specs))
            #tqdm.write(str(singular_transformation_outputs))

            #tqdm.write("parameters:")
            
            singular_parameters = get_component_parameters(ontology, singular_component)

            singular_overridden_parameters = get_component_overridden_paramspecs(ontology, workflow_graph, singular_component)
            singular_parameters = perform_param_substitution(graph=workflow_graph, parameters=singular_parameters,
                                                                implementation=singular_component_implementation,
                                                                inputs=singular_transformation_inputs,
                                                                intent_graph=intent_graph)
            
            singular_param_specs = assign_to_parameter_specs(workflow_graph, singular_parameters)
            singular_param_specs.update(singular_overridden_parameters)
            #tqdm.write(str(singular_param_specs))

            

            singular_step = add_step(workflow_graph, workflow,
                                singular_step_name,
                                singular_component,
                                singular_param_specs,
                                task_order, previous_step,
                                [previous_node],
                                singular_transformation_outputs)
            run_component_transformation(ontology, workflow_graph, singular_component,
                                            [previous_node], singular_transformation_outputs, singular_param_specs)


            train_dataset_index = identify_data_io(ontology, singular_output_specs, train=True, return_index=True)
            
            test_dataset_index = identify_data_io(ontology, singular_output_specs, test=True, return_index=True)

            if train_dataset_index is not None:
                train_dataset_node =  singular_transformation_outputs[train_dataset_index]
            if test_dataset_index is not None:
                test_dataset_node = singular_transformation_outputs[test_dataset_index]
                
            previous_step = singular_step
            previous_train_step = singular_step
            previous_test_step = singular_step
            
            task_order += 1

        else:

            train_step_name = get_step_name(workflow_name, task_order, train_component)

            train_component_implementation = get_component_implementation(ontology, train_component)

            train_input_specs = get_implementation_input_specs(ontology, train_component_implementation,max_imp_level)
            train_input_data_index = identify_data_io(ontology, train_input_specs, return_index=True)
            train_transformation_inputs = [ab[f'{train_step_name}-input_{i}'] for i in range(len(train_input_specs))]
            train_transformation_inputs[train_input_data_index] = train_dataset_node 
            annotate_ios_with_specs(ontology, workflow_graph, train_transformation_inputs,
                                    train_input_specs)

            #tqdm.write("Sepecs train input:")
            #tqdm.write(str(train_transformation_inputs))
            #tqdm.write(str(train_input_specs))
            train_output_specs = get_implementation_output_specs(ontology, train_component_implementation)
            train_output_model_index = identify_model_io(ontology, train_output_specs, return_index=True)
            train_output_data_index = identify_data_io(ontology, train_output_specs, return_index=True)
            train_transformation_outputs = [ab[f'{train_step_name}-output_{i}'] for i in range(len(train_output_specs))]
            annotate_ios_with_specs(ontology, workflow_graph, train_transformation_outputs,
                                    train_output_specs)
            
            #tqdm.write("Sepecs train output:")
            #tqdm.write(str(train_transformation_outputs))
            #tqdm.write(str(train_output_specs))

            #tqdm.write("parameters:")

            train_parameters = get_component_parameters(ontology, train_component)
            train_parameters = perform_param_substitution(graph=workflow_graph, implementation=train_component_implementation,
                                                            parameters=train_parameters,
                                                            intent_graph=intent_graph,
                                                            inputs=train_transformation_inputs)
            train_overridden_paramspecs = get_component_overridden_paramspecs(ontology, workflow_graph, train_component)
            train_param_specs = assign_to_parameter_specs(workflow_graph, train_parameters)
            train_param_specs.update(train_overridden_paramspecs)
            #tqdm.write(str(train_param_specs))
            train_step = add_step(workflow_graph, workflow,
                                train_step_name,
                                train_component,
                                train_param_specs,
                                task_order, previous_train_step,
                                train_transformation_inputs,
                                train_transformation_outputs)

            previous_train_step = train_step 

            run_component_transformation(ontology, workflow_graph, train_component, train_transformation_inputs,
                                        train_transformation_outputs, train_param_specs)

            if train_output_data_index is not None:
                train_dataset_node = train_transformation_outputs[train_output_data_index]

            previous_step = train_step
            previous_node = train_dataset_node

            task_order += 1

            if test_dataset_node is not None:

                #tqdm.write("test dataset node")

                test_step_name = get_step_name(workflow_name, task_order, test_component)

                test_input_specs = get_implementation_input_specs(ontology,
                                                                get_component_implementation(ontology, test_component),max_imp_level)
                test_input_data_index = identify_data_io(ontology, test_input_specs, test=True, return_index=True)
                test_input_model_index = identify_model_io(ontology, test_input_specs, return_index=True)
                test_transformation_inputs = [ab[f'{test_step_name}-input_{i}'] for i in range(len(test_input_specs))]
                test_transformation_inputs[test_input_data_index] = test_dataset_node
                if train_output_model_index is not None:
                    test_transformation_inputs[test_input_model_index] = train_transformation_outputs[train_output_model_index]
                annotate_ios_with_specs(ontology, workflow_graph, test_transformation_inputs,
                                        test_input_specs)
                
                #tqdm.write("Sepecs test input:")
                #tqdm.write(str(test_transformation_inputs))
                #tqdm.write(str(test_input_specs))
                
                test_implementation = get_component_implementation(ontology, test_component)
                test_output_specs = get_implementation_output_specs(ontology, test_implementation)
                test_output_data_index = identify_data_io(ontology, test_output_specs, return_index=True)
                test_transformation_outputs = [ab[f'{test_step_name}-output_{i}'] for i in range(len(test_output_specs))]
                annotate_ios_with_specs(ontology, workflow_graph, test_transformation_outputs,
                                        test_output_specs)
                
                #tqdm.write("Sepecs test output:")
                #tqdm.write(str(test_transformation_outputs))
                #tqdm.write(str(test_output_specs))

                #tqdm.write("parameters:")

                previous_test_steps = [previous_test_step, train_step] if not same else [previous_test_step]
                test_parameters = get_component_parameters(ontology, test_component)
                test_component_implementation = get_component_implementation(ontology, test_component) if test_component else None
                test_parameters = perform_param_substitution(workflow_graph,
                                                             test_component_implementation,
                                                             test_parameters,
                                                             test_transformation_inputs,
                                                             intent_graph=intent_graph)
                test_overridden_paramspecs = get_component_overridden_paramspecs(ontology, workflow_graph, train_component)
                test_param_specs = assign_to_parameter_specs(workflow_graph, test_parameters)
                test_param_specs.update(test_overridden_paramspecs)
                #tqdm.write(str(test_param_specs))

                test_step = add_step(workflow_graph, workflow,
                                    test_step_name,
                                    test_component,
                                    test_param_specs,
                                    task_order, previous_test_steps,
                                    test_transformation_inputs,
                                    test_transformation_outputs)

                run_component_transformation(ontology, workflow_graph, test_component, test_transformation_inputs,
                                            test_transformation_outputs, test_param_specs)
                
                test_dataset_node = test_transformation_outputs[test_output_data_index]
                previous_test_step = test_step
                task_order += 1
            
    
    if test_dataset_node is not None:
        #tqdm.write("saver state")
        saver_component = cb.term('component-csv_local_writer')
        saver_step_name = get_step_name(workflow_name, task_order, saver_component)
        saver_parameters = get_component_parameters(ontology, saver_component)
        saver_implementation = get_component_implementation(ontology, saver_component)
        saver_parameters = perform_param_substitution(workflow_graph, saver_implementation, saver_parameters, [test_dataset_node])
        saver_overridden_paramspecs = get_component_overridden_paramspecs(ontology, workflow_graph, saver_component)
        saver_param_specs = assign_to_parameter_specs(workflow_graph, saver_parameters)
        saver_param_specs.update(saver_overridden_paramspecs)
        add_step(workflow_graph,
                workflow,
                saver_step_name,
                saver_component,
                saver_param_specs,
                task_order,
                previous_test_step, [test_dataset_node], [])

    return workflow_graph, workflow



def build_workflows(ontology: Graph, shape_graph, intent_graph: Graph, destination_folder: str, log: bool = False) -> None:
    
    dataset, task, algorithm, intent_iri = get_intent_info(intent_graph)

    component_threshold = float(next(intent_graph.objects(intent_iri, tb.has_component_threshold), None))
    max_imp_level = int(next(intent_graph.objects(intent_iri, tb.has_complexity), None))

    if log:
        tqdm.write(f'Intent: {intent_iri.fragment}')
        tqdm.write(f'Dataset: {dataset.fragment}')
        tqdm.write(f'Task: {task.fragment}')
        tqdm.write(f'Algorithm: {algorithm.fragment if algorithm is not None else [algo.fragment for algo in get_algorithms_from_task(ontology, task)]}')
        tqdm.write(f'Preprocessing Component Percentage Threshold: {component_threshold*100}%')
        tqdm.write(f'Maximum complexity level: {max_imp_level}')
        tqdm.write('-------------------------------------------------')

    all_cols = get_inputs_all_columns(ontology, [dataset])
    cat_cols = get_inputs_categorical_columns(ontology, [dataset])
    num_cols = get_inputs_numeric_columns(ontology, [dataset])
    
    exp_params = get_exposed_parameters(ontology, task, algorithm)

    for exp_param in exp_params:
        option_columns = []
        if 'CATEGORICAL' in exp_param['value']:
            option_columns = cat_cols
        elif 'NUMERICAL' in exp_param['value']:
            option_columns = num_cols
        else:
            option_columns = all_cols

        if 'COMPLETE' in exp_param['value']:
            option_columns.append('<RowID>')

        if 'INCLUDED' in exp_param['condition']:
            param_val = []
            col_num = int(input(f"How many columns do you want to enter for {exp_param['label']} parameter?"))
            for i in range(col_num):
                param_val.append(input(f"Enter a value for {exp_param['label']} from the following: {option_columns}"))
        else:
            param_val = input(f"Enter a value for {exp_param['label']} from the following: {option_columns}")

        intent_graph.add((intent_iri, tb.specifiesValue, Literal(param_val)))
        intent_graph.add((Literal(param_val), tb.forParameter, exp_param['exp_param']))

    algs = algorithm if not algorithm is None else get_algorithms_from_task_constrained(ontology,shape_graph,task)
    tqdm.write(str(algs))

    
    pot_impls = []
    for al in algs:
        pot_impls.extend(get_potential_implementations_constrained(ontology, shape_graph, al))
    
    tqdm.write(str(pot_impls))

    impls_with_shapes = [
        (implementation, get_implementation_input_specs(ontology, implementation,max_imp_level))
        for implementation in pot_impls]
    
    components = [
        (c, impl, inputs)
        for impl, inputs in impls_with_shapes
        for c in get_implementation_components_constrained(ontology, shape_graph, impl)
    ]


    if log:
        for component, implementation, inputs in components:
            tqdm.write(f'Component: {component.fragment} ({implementation.fragment})')
            for im_input in inputs:
                tqdm.write(f'\tInput: {[x.fragment for x in im_input]}')
        tqdm.write('-------------------------------------------------')

    workflow_order = 0


    for component, implementation, inputs in tqdm(components, desc='Components', position=1):
        if log:
            tqdm.write(f'Component: {component.fragment} ({implementation.fragment})')
        shapes_to_satisfy = identify_data_io(ontology, inputs)
        assert shapes_to_satisfy is not None and len(shapes_to_satisfy) > 0
        if log:
            tqdm.write(f'\tData input: {[x.fragment for x in shapes_to_satisfy]}')

        unsatisfied_shapes = [shape for shape in shapes_to_satisfy if
                              not satisfies_shape(ontology, ontology, shape, dataset)]
        print(f'UNSATISFIED SHAPES: {unsatisfied_shapes}')

        available_transformations = {
            shape: get_implementation_components_constrained(ontology,shape_graph,imp)
            for shape in unsatisfied_shapes
            for imp in find_implementations_to_satisfy_shape_constrained(ontology, shape_graph, shape, exclude_appliers=True)

        }
        print(f'AVAILABLE TRANSFORMATIONS: {available_transformations}')
        for tr, methods in available_transformations.items():

            best_components = get_best_components(ontology, task, methods, dataset, component_threshold)

            available_transformations[tr] = list(best_components.keys())

        print(f'REFINED TRANSFORMATIONS: {available_transformations}')
                    


        if log:
            tqdm.write(f'\tUnsatisfied shapes: ')
            for shape, transformations in available_transformations.items():
                tqdm.write(f'\t\t{shape.fragment}: {[x.fragment for x in transformations]}')

        transformation_combinations = list(
            enumerate(itertools.product(*available_transformations.values())))

        transformation_combinations_constrained = prune_workflow_combinations(ontology, shape_graph, transformation_combinations,component)
        #ontology.serialize('./tmp.ttl',format="turtle")

        if log:
            tqdm.write(f'\tTotal combinations: {len(transformation_combinations_constrained)}')

        for i, transformation_combination in tqdm(transformation_combinations_constrained, desc='Transformations', position=0,
                                                  leave=False):
            if log:
                tqdm.write(
                    f'\t\tCombination {i + 1} / {len(transformation_combinations_constrained)}: {[x.fragment for x in transformation_combination]}')

            workflow_name = f'workflow_{workflow_order}_{intent_iri.fragment}_{uuid.uuid4()}'.replace('-', '_')
            
            wg, w = build_general_workflow(workflow_name, ontology, dataset, component,
                                           transformation_combination, intent_graph = intent_graph)

            wg.add((w, tb.generatedFor, intent_iri))
            wg.add((intent_iri, RDF.type, tb.Intent))

            if log:
                tqdm.write(f'\t\tWorkflow {workflow_order}: {w.fragment}')
            wg.serialize(os.path.join(destination_folder, f'{workflow_name}.ttl'), format='turtle')
            workflow_order += 1


def interactive():
    intent_graph = get_graph_xp()
    intent = input('Introduce the intent name [ClassificationIntent]: ') or 'VisualizationIntent' #or 'ClassificationIntent'
    data = input('Introduce the dataset name [titanic.csv]: ') or 'titanic.csv'
    task = input('Introduce the task name [Classification]: ') or 'Classification'


    intent_graph.add((ab.term(intent), RDF.type, tb.Intent))
    intent_graph.add((ab.term(intent), tb.overData, ab.term(data)))
    intent_graph.add((cb.term(task), tb.tackles, ab.term(intent)))


    ontology = get_ontology_graph()

    if task == 'DataVisualization':
        algos = [alg.fragment for alg in get_algorithms_from_task(ontology, cb.term(task))]
        vis_algorithm = str(input(f'Choose a visualization algorithm from the following (case-sensitive):{algos}'))
        if vis_algorithm is not None:
            intent_graph.add((ab.term(intent), tb.specifies, cb.term(vis_algorithm)))

    component_percentage = float(input('Choose a threshold component percentage (for the preprocessing components) [100, 75, 50, 25] (%): ') or 100)/100.0
    complexity = int(input("Choose the complexity of the generated workflows [0,1,2]: ") or 2)

    intent_graph.add((ab.term(intent), tb.has_component_threshold, Literal(component_percentage)))
    intent_graph.add((ab.term(intent), tb.has_complexity, Literal(complexity)))

    folder = input('Introduce the folder to save the workflows: ')
    if folder == '':
        folder = f'./workflows/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}/'
        tqdm.write(f'No folder introduced, using default ({folder})')
    if not os.path.exists(folder):
        tqdm.write('Directory does not exist, creating it')
        os.makedirs(folder)

    shape_graph = Graph()
    t = time.time()
    build_workflows(ontology, shape_graph, intent_graph, folder, log=True)
    t = time.time() - t

    print(f'Workflows built in {t} seconds')
    print(f'Workflows saved in {folder}')


#interactive()