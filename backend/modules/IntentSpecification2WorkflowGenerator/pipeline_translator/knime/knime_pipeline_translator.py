import os
import sys
import tempfile
import zipfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Tuple, Dict, List
import jinja2

from tqdm import tqdm

translator_dir = os.path.join(os.path.abspath(os.path.join('..')))
sys.path.append(translator_dir)

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["pipeline_translator/knime/templates", "templates"])) #the double path ensures expected performance on terminal and api execution
from pipeline_translator.core.translator_common_functions import *

from rdflib import Graph, URIRef, RDF, XSD

try:
    import easygui # type: ignore
except ImportError:
    easygui = None



def get_knime_properties(ontology: Graph, implementation: URIRef) -> Dict[str, str]:
    results = {}
    for p, o in ontology.predicate_objects(implementation):
        if p.fragment.startswith('knime'):
            results[p.fragment[6:]] = o.value
            # print(f"THIS: {p.fragment[6:]} ---> {o.value}")
    return results

def update_param_hierarchy(param_dict:Dict, path: List[str], element):

    if len(path) == 0:
        if element[0] != "$$SKIP$$":
            param_dict['elements'].append(element)
    else:
        level = path.pop(0)
        if level not in param_dict['folders']:
            param_dict['folders'][level] = {
                'folders': {},
                'elements': []
            }
        param_dict[level] = update_param_hierarchy(param_dict['folders'][level], path, element)
    
    return param_dict


def get_config_parameters(ontology: Graph, workflow_graph: Graph, step: URIRef):
    types = {
        XSD.string: 'xstring',
        cb.term('char'): 'xchar',
        XSD.int: 'xint',
        XSD.integer: 'xint',
        XSD.long: 'xlong',
        XSD.float: 'xdouble',
        XSD.double: 'xdouble',
        XSD.boolean: 'xboolean',
        RDF.List: ''
    }

    parameters = get_step_parameters(ontology, workflow_graph, step)
    param_dict = {'folders': {},
                  'elements': []}
    

    for key, value, path, value_type in parameters:
        if value_type == RDF.List:
            param_value = value.replace("[", "").replace("]", "").replace("\'", "").replace(" ","").split(',')
            arrayPath = path+'/'+key
            parameters.append( ("array-size", str(len(param_value)), arrayPath, XSD.int) )
            for i,param in enumerate(param_value):
                parameters.append((str(i),param,arrayPath,XSD.string))
        else:
            if value is None or (isinstance(value, str) and value.lower() == 'none'):
                param_value = None
            else:
                param_value = value

            param_dict = update_param_hierarchy(param_dict, path.split('/'),(str(key),param_value,types[value_type]))
    return param_dict


def create_step_file(ontology: Graph, workflow_graph: Graph, step: URIRef, folder, iterator: int) -> str:

    component, implementation = get_step_component_implementation(ontology, workflow_graph, step)
    properties = get_knime_properties(ontology, implementation)

    
    conf_params = get_config_parameters(ontology, workflow_graph, step)
    num_ports = get_number_of_output_ports(ontology, workflow_graph, step)

    step_template = environment.get_template("step.py.jinja")
    step_file = step_template.render(properties = properties,
                                     parameters = conf_params,
                                     num_ports = num_ports)
    
    path_name = properties["node-name"].replace('(', '_').replace(')', '_')
    
    subfolder_name = f'{path_name} (#{iterator})'
    subfolder = os.path.join(folder, subfolder_name)
    os.mkdir(subfolder)

    with open(os.path.join(subfolder, 'settings.xml'), encoding='UTF-8', mode='w') as file:
        file.write(step_file)

    return subfolder_name


def create_workflow_metadata_file(workflow_graph: Graph, folder: str) -> None:
    author = 'ODIN'
    date = datetime.today().strftime('%d/%m/%Y')
    workflow_name = next(workflow_graph.subjects(RDF.type, tb.Workflow, True)).fragment
    title = f'{get_workflow_intent_name(workflow_graph)} (Workflow {get_workflow_intent_number(workflow_graph)})'
    description = f'This workflow was automatically created from the logical workflow {workflow_name}.'
    url = 'ExtremeXP https://extremexp.eu/'
    tags = 'model training, training, testing'

    metadata_template = environment.get_template("metadata.py.jinja")
    workflow_metadata_file = metadata_template.render(author = author,
                                                      date = date,
                                                      workflow_name = workflow_name,
                                                      title = title,
                                                      description = description,
                                                      url = url,
                                                      tags = tags) 
    
    with open(os.path.join(folder, 'workflowset.meta'), 'w') as f:
        f.write(workflow_metadata_file)


def get_nodes_config(step_paths: List[str]) -> ET.Element:
    root = ET.Element('config', {'key': 'nodes'})
    for i, step in enumerate(step_paths):
        node_cofig = ET.SubElement(root, 'config', {'key': f'node_{i}'})
        ET.SubElement(node_cofig, 'entry', {'key': 'id', 'type': 'xint', 'value': str(i)})
        ET.SubElement(node_cofig, 'entry', {'key': 'node_settings_file', 'type': 'xstring',
                                            'value': f'{step}/settings.xml'})
        ET.SubElement(node_cofig, 'entry', {'key': 'node_is_meta', 'type': 'xboolean', 'value': 'false'})
        ET.SubElement(node_cofig, 'entry', {'key': 'node_type', 'type': 'xstring', 'value': 'NativeNode'})
        ET.SubElement(node_cofig, 'entry', {'key': 'ui_classname', 'type': 'xstring',
                                            'value': 'org.knime.core.node.workflow.NodeUIInformation'})
        ui_settings = ET.SubElement(node_cofig, 'config', {'key': 'ui_settings'})
        bounds = ET.SubElement(ui_settings, 'config', {'key': 'extrainfo.node.bounds'})

        applier = any(x in step.lower() for x in ['appl', 'predictor'])
        ET.SubElement(bounds, 'entry', {'key': 'array-size', 'type': 'xint', 'value': '4'})
        ET.SubElement(bounds, 'entry', {'key': '0', 'type': 'xint', 'value': str((i + 1) * 150)})  # x
        ET.SubElement(bounds, 'entry', {'key': '1', 'type': 'xint', 'value': '400' if applier else '200'})  # y
        ET.SubElement(bounds, 'entry', {'key': '2', 'type': 'xint', 'value': '75'})  # width
        ET.SubElement(bounds, 'entry', {'key': '3', 'type': 'xint', 'value': '80'})  # height

    return root


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


def get_connections_config(workflow_graph: Graph, steps: List[URIRef]) -> ET.Element:
    root = ET.Element('config', {'key': 'connections'})
    connections = get_workflow_connections(workflow_graph)
    for i, (source, destination, source_port, destination_port) in enumerate(connections):
        connection_config = ET.SubElement(root, 'config', {'key': f'connection_{i}'})
        ET.SubElement(connection_config, 'entry',
                      {'key': 'sourceID', 'type': 'xint', 'value': str(steps.index(source))})
        ET.SubElement(connection_config, 'entry', {'key': 'sourcePort', 'type': 'xint', 'value': str(source_port + 1)})
        ET.SubElement(connection_config, 'entry',
                      {'key': 'destID', 'type': 'xint', 'value': str(steps.index(destination))})
        ET.SubElement(connection_config, 'entry',
                      {'key': 'destPort', 'type': 'xint', 'value': str(destination_port + 1)})
        ET.SubElement(connection_config, 'entry', {'key': 'ui_classname', 'type': 'xstring',
                                                   'value': 'org.knime.core.node.workflow.ConnectionUIInformation'})
        ui_settings = ET.SubElement(connection_config, 'config', {'key': 'ui_settings'})
        ET.SubElement(ui_settings, 'entry', {'key': 'extrainfo.conn.bendpoints_size', 'type': 'xint', 'value': '0'})
    return root


def get_author_config() -> ET.Element:
    root = ET.Element('config', {'key': 'authorInformation'})
    ET.SubElement(root, 'entry', {'key': 'authored-by', 'type': 'xstring', 'value': 'ODIN'})
    ET.SubElement(root, 'entry', {'key': 'authored-when', 'type': 'xstring',
                                  'value': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %z')})
    ET.SubElement(root, 'entry', {'key': 'lastEdited-by', 'type': 'xstring', 'value': 'ODIN'})
    ET.SubElement(root, 'entry', {'key': 'lastEdited-when', 'type': 'xstring',
                                  'value': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %z')})
    return root


def create_workflow_file(workflow_graph: Graph, steps: List[URIRef], step_paths: List[str],
                         folder: str) -> None:
    node_config = get_nodes_config(step_paths)
    connections_config = get_connections_config(workflow_graph, steps)
    author_config = get_author_config()

    root = ET.Element('config', {'xmlns': 'http://www.knime.org/2008/09/XMLConfig',
                                 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                 'xsi:schemaLocation': 'http://www.knime.org/2008/09/XMLConfig http://www.knime.org/XMLConfig_2008_09.xsd',
                                 'key': 'workflow.knime'})

    ET.SubElement(root, 'entry', {'key': 'created_by', 'type': 'xstring', 'value': '4.7.3.v202305100921'})
    ET.SubElement(root, 'entry', {'key': 'created_by_nightly', 'type': 'xboolean', 'value': 'false'})
    ET.SubElement(root, 'entry', {'key': 'version', 'type': 'xstring', 'value': '4.1.0'})
    ET.SubElement(root, 'entry', {'key': 'name', 'type': 'xstring', 'isnull': 'true', 'value': ''})
    ET.SubElement(root, 'entry', {'key': 'customDescription', 'type': 'xstring', 'isnull': 'true', 'value': ''})
    ET.SubElement(root, 'entry', {'key': 'state', 'type': 'xstring', 'value': 'CONFIGURED'})
    ET.SubElement(root, 'config', {'key': 'workflow_credentials'})

    root.append(node_config)
    root.append(connections_config)
    root.append(author_config)

    tree = ET.ElementTree(root)
    ET.indent(tree, space='    ')
    tree.write(os.path.join(folder, 'workflow.knime'), encoding='UTF-8', xml_declaration=True)


def package_workflow(folder: str, destination: str) -> None:
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, folder)
                workflow_name = os.path.splitext(os.path.basename(destination))[0]
                zipf.write(file_path, arcname=os.path.join(workflow_name, archive_path))


def translate_graph(ontology: Graph, source_path: str, destination_path: str, keep_folder=False) -> None:
    tqdm.write('Creating new workflow')

    tqdm.write('\tCreating temp folder: ', end='')
    temp_folder = tempfile.mkdtemp()
    tqdm.write(temp_folder)

    tqdm.write('\tLoading workflow:', end=' ')
    graph = load_workflow(source_path)
    tqdm.write(next(graph.subjects(RDF.type, tb.Workflow, True)).fragment)

    tqdm.write('\tCreating workflow metadata file')
    create_workflow_metadata_file(graph, temp_folder)

    tqdm.write('\tBuilding steps')
    steps = get_workflow_steps(graph)
    step_paths = []
    for i, step in enumerate(steps):
        step_paths.append(create_step_file(ontology, graph, step, temp_folder, i))

    tqdm.write('\tCreating workflow file')
    create_workflow_file(graph, steps, step_paths, temp_folder)

    tqdm.write('\tCreating zip file')
    package_workflow(temp_folder, destination_path)

    if keep_folder:
        tqdm.write('\tCopying temp folder')
        shutil.copytree(temp_folder, destination_path[:-4])

    tqdm.write('\tRemoving temp folder')
    shutil.rmtree(temp_folder)
    tqdm.write('Done')
    tqdm.write('-' * 50)


def translate_graph_folder(ontology: Graph, source_folder: str, destination_folder: str, keep_folder=False) -> None:
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    assert os.path.exists(source_folder)

    workflows = [f for f in os.listdir(source_folder) if f.endswith('.ttl')]
    for workflow in tqdm(workflows):
        source_path = os.path.join(source_folder, workflow)
        destination_path = os.path.join(destination_folder, workflow[:-4] + '.knwf')
        translate_graph(ontology, source_path, destination_path, keep_folder)


def interactive():
    if easygui is None:
        source_folder = input('Source folder: ')
        destination_folder = input('Destination folder: ')
    else:
        source_folder = easygui.diropenbox('Source folder', 'Source folder', '.')
        print(f'Source folder: {source_folder}')
        destination_folder = easygui.diropenbox('Destination folder', 'Destination folder', '.')
        print(f'Destination folder: {destination_folder}')

    keep_folder = input('Keep workflows in folder format? [Y/n]: ').lower() not in ['n', 'no']

    translate_graph_folder(get_ontology(), source_folder, destination_folder, keep_folder=keep_folder)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        translate_graph_folder(get_ontology(), sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        translate_graph(get_ontology(), sys.argv[2], sys.argv[3], keep_folder=True)
    else:
        print('Interactive usage.')
        print('For non-interactive usage, use:')
        print('\tpython workflow_translator.py <source_folder> <destination_folder>')
        print('\tpython workflow_translator.py --keep <source_folder> <destination_folder>')
        interactive()
