import itertools
import sys
from pathlib import Path
from typing import List
import uuid
from tqdm import tqdm
import re
from rdflib import RDF, Graph, Literal, URIRef
import time

p = Path().absolute() / '../..'
sys.path.append(p.resolve().as_posix())

from pipeline_generator.optimized_pipeline_generator import get_intent_info, get_implementation_prerquisites,get_implementation_components_constrained 
from pipeline_generator.optimized_pipeline_generator import get_best_components, prune_workflow_combinations, build_general_workflow, get_potential_implementations_constrained

from common.common import ab, tb, cb, get_graph_xp

def generate_intent(file: Path) -> Graph:
    intent_graph = get_graph_xp()
    intent = ab.term(f'Intent_{file.stem}')
    intent_graph.add((intent, RDF.type, tb.Intent))
    intent_graph.add((intent, tb.has_complexity, Literal(3)))
    intent_graph.add((intent, tb.has_component_threshold, Literal(1.0)))
    intent_graph.add((intent, tb.overData, ab.term(file.name)))
    intent_graph.add((cb.MainTask, tb.tackles, intent))

    return intent_graph

    
def get_combinations(ontology: Graph, shape_graph: Graph, intent_graph: Graph, pot_impls, log: bool = False):
    dataset, task, algorithm, intent_iri = get_intent_info(intent_graph)
    max_imp_level = int(next(intent_graph.objects(intent_iri, tb.has_complexity), None))
    component_threshold = float(next(intent_graph.objects(intent_iri, tb.has_component_threshold), None))

    if log:
        tqdm.write(f'Preprocessing Component Percentage Threshold: {component_threshold*100}%')
        tqdm.write(f'Maximum complexity level: {max_imp_level}')
        tqdm.write('-------------------------------------------------')

    options = []
    for imp in pot_impls:
        result = get_implementation_prerquisites(ontology, shape_graph, dataset, imp, max_imp_level, log=False)
        if not result is None and result != []:
            options.append(result)

    if log:
        tqdm.write(f'\tTotal combinations: {len(options)}')
    
    return options[0]

def get_prep_comp(ontology, shape_graph, dataset, component_threshold, task, plan):
    if isinstance(plan, URIRef):
        available_components = get_implementation_components_constrained(ontology, shape_graph, plan)
        best_components = get_best_components(ontology, task, available_components, dataset, component_threshold)
        return [list(best_components.keys())]
    else: #tuple
        elms = []
        for element in plan:
            elms.extend(get_prep_comp(ontology, shape_graph, dataset, component_threshold, task,element))
        return elms

def build_workflows_combinations(ontology: Graph, shape_graph:Graph, component_threshold, intent_graph: Graph, plans, log: bool = False) -> List[Graph]:

    dataset, task, algorithm, intent_iri = get_intent_info(intent_graph)
    workflow_order = 0
    workflows = []

    i = 0
    for transformation_combination in plans:
        tqdm.write("Building")
        tqdm.write(str(i))

        if log:
            tqdm.write(str(i))
                #f'\t\tCombination {i + 1} / ?: {[x.fragment for x in transformation_combination]}')

        prep_components = get_prep_comp(ontology, shape_graph, dataset, component_threshold, task, transformation_combination)

        component_combinations = itertools.product(*prep_components)

        for component_combination in component_combinations:
            tqdm.write(f"Building workflow {i}")
            workflow_name = f'workflow_{workflow_order}_{intent_iri.fragment}_{uuid.uuid4()}'.replace('-', '_')
        
            wg, w = build_general_workflow(workflow_name, ontology, dataset, component_combination[-1],
                                            component_combination[:-1], intent_graph = intent_graph)

            wg.add((w, tb.generatedFor, intent_iri))
            wg.add((intent_iri, RDF.type, tb.Intent))

            if log:
                tqdm.write(f'\t\tWorkflow {workflow_order}: {w.fragment}')

            workflows.append(wg)
            workflow_order += 1
            i += 1
    return workflows


def run_experiment(ontology_path:Path, data_path:Path, experiment_folder:Path):

    ontology = get_graph_xp().parse(location=ontology_path.as_uri())
    data = Graph().parse(location=data_path.as_uri())
    data.serialize('test.ttl', format='turtle')
    ontology = ontology + data
    pot_impls = get_potential_implementations_constrained(ontology,Graph(),cb['MainAlgorithm'])
    intent_graph = generate_intent(data_path)

    t1 = time.perf_counter()
    tcc = get_combinations(ontology,Graph(),intent_graph,pot_impls,log=False)
    t2 = time.perf_counter()
    workflows = build_workflows_combinations(ontology, Graph(), 1.0, intent_graph,tcc, log=False)
    t3 = time.perf_counter()

    t_comb = t2 - t1
    t_wkfw = t3 - t2

    for i, w in enumerate(workflows[:10]):
        w.serialize(experiment_folder / f'Workflow{i}.ttl')

    return t_comb, t_wkfw, len(workflows)

def run_experiment_suite(source_folder: str, data_file: str, destination_folder: str):
    cboxes = [f for f in Path(source_folder).iterdir() if f.suffix == '.ttl']
    cboxes.sort(reverse=True)
    print(cboxes)
    regex = r'cbox_(\d+)_(\d+)i_(\d+)sh_(\d+)cpi.ttl'

    result_file = open(Path(destination_folder)/'results.csv', 'w')
    result_file.write('main_impls,prep_levels,i_shapes,cpi,time_comb, time_work, num_workflows\n')

    for cbox in tqdm(cboxes, desc='Experiments', position=2):
        experiment_folder = Path(destination_folder) / 'workflows' /  cbox.stem
        Path(experiment_folder).mkdir(exist_ok=True)

        data_file = Path(data_file).resolve()

        match = re.match(regex, cbox.name)
        m_impl = int(match.group(1))
        c_impl = int(match.group(2))
        i_sh = int(match.group(3))
        cpi = int(match.group(4))

        tqdm.write(f'Running experiment for {m_impl}/{c_impl}/{i_sh}/{cpi}')
        tqdm.write(f'\t# Components: {(m_impl + c_impl)*cpi}')
        tqdm.write(f'\t# Requirements per component: {i_sh}')
        tqdm.write(f'\t# Components per implementation: {cpi}')

        t_c, t_w, nw = run_experiment(Path(source_folder).resolve() / cbox.name , data_file, experiment_folder)
        tqdm.write(f'--------------------------------------------------------------------------------------------')

        result_file.write(f'{m_impl},{c_impl},{i_sh},{cpi},{t_c},{t_w},{nw}\n')


if __name__ == '__main__':
    run_experiment_suite('./fake_cboxes', './annotated_datasets/T1016_SystemNetworkConfigurationDiscovery.ttl' ,'./results')