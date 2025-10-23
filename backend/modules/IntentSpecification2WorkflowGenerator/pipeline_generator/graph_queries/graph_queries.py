from typing import Dict, List, Set, Tuple, Type, Union, Literal as Lit
from rdflib import Graph, URIRef


from common import *

def get_data_input(graph:Graph, inputs:list[URIRef]):
    data_input = next(i for i in inputs if (i, RDF.type , dmop.TabularDataset) in graph or (i, RDF.type , dmop.TensorDataset) in graph)
    return data_input


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


def targets_dataset(ontology:Graph, shape:URIRef):
    query = f"""
            PREFIX sh: <{SH}>
            PREFIX rdfs: <{RDFS}>
            PREFIX tb: <{tb}>

            ASK {{
                {{
                {shape.n3()} a sh:NodeShape ;
                    sh:targetClass ?dataset .
                ?dataset rdfs:subClassOf tb:Dataset .
                }}
            }}
    """

    return ontology.query(query).askAnswer


#TODO: this function is a monster. Refactoring would be nice
def identify_data_io(ontology: Graph, ios: List[Tuple[URIRef,List[URIRef]]], train: bool = False, test: bool = False, return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, (io_spec, io_shapes) in enumerate(ios):
        for io_shape in io_shapes:
            if (targets_dataset(ontology, io_shape) 
                or (io_shape, SH.targetClass, cb.TabularDatasetShape) in ontology 
                or io_shape.fragment == "TabularDatasetShape") or True:

                if test:
                    test_query = f'''
                    PREFIX sh: <{SH}>
                    PREFIX rdfs: <{RDFS}>
                    PREFIX cb: <{cb}>
                    PREFIX dmop: <{dmop}>

                    ASK {{
                        {{
                        {io_shape.n3()} a sh:NodeShape ;
                                        sh:targetClass ?class ;
                                        sh:property [
                                            sh:path dmop:isTestDataset ;
                                            sh:hasValue true
                                        ] .
                            ?class rdfs:subClassOf tb:Dataset
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
                                        sh:targetClass ?class ;
                                        sh:property [
                                            sh:path dmop:isTrainDataset ;
                                            sh:hasValue true
                                        ] .
                        ?class rdfs:subClassOf tb:Dataset
                        }}
                    }}
                    '''
                    result = ontology.query(train_query).askAnswer
                    if result:
                        return i if return_index else io_shapes
                
                if not train and not test:
                    return i if return_index else io_shapes
            
def identify_model_io(ontology: Graph, ios:List[Tuple[URIRef,List[URIRef]]], return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, (io_spec, io_shapes) in enumerate(ios):
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
        SELECT ?parameter ?value ?position ?condition
        WHERE {{
            {component.n3()} tb:hasImplementation ?implementation .
            ?implementation tb:hasParameter ?parameter .
            ?parameter tb:has_position ?position ;
                       tb:has_defaultvalue ?value ;
                       tb:has_condition ?condition .
            FILTER NOT EXISTS {{
                ?parameter tb:specifiedBy ?parameterSpecification .
            }}
        }}
        ORDER BY ?position
    """
    results = ontology.query(parameters_query).bindings
    return {param['parameter']: (param['value'],param['position'], param['condition']) for param in results}


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
    data_input = get_data_input(graph,inputs)
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
    
    data_input = get_data_input(graph,inputs)
    if data_input is None:
        return ""

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
    
    data_input = get_data_input(graph, inputs)

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
    data_input = get_data_input(graph, inputs)
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


def get_inputs_categorical_columns(graph: Graph, inputs: List[URIRef], includeTarget=True) -> str:
    data_input = get_data_input(graph, inputs)

    categ_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isCategorical true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
            {"?column dmop:isLabel false ." if not includeTarget else ""}
        }}
    """
    columns = graph.query(categ_query).bindings

    return [x['label'].value for x in columns]

def get_inputs_feature_types(graph: Graph, inputs: List[URIRef]) -> Set[Type]:
    data_input = get_data_input(graph, inputs)

    if data_input is None:
        return set()
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



def get_engine(graph: Graph, implementation:URIRef):
    return next(graph.objects(implementation, tb.has_engine, unique=True),None)


def get_implementation_engine_compatibility(ontology:Graph, implementation: URIRef):
    return set(ontology.objects(implementation, tb.compatibleWith))


