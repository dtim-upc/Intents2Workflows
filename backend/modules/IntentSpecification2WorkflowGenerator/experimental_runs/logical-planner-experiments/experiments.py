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

from pipeline_generator.pipeline_generator import get_potential_implementations_constrained, build_workflows

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

def run_experiment(ontology_path:Path, data_path:Path, experiment_folder:Path):

    ontology = get_graph_xp().parse(location=ontology_path.as_uri())
    data = Graph().parse(location=data_path.as_uri())
    data.serialize('test.ttl', format='turtle')
    ontology = ontology + data
    pot_impls = get_potential_implementations_constrained(ontology,Graph(),cb['MainAlgorithm'])
    intent_graph = generate_intent(data_path)

    t1 = time.perf_counter()
    #tcc = get_combinations(ontology,Graph(),intent_graph,pot_impls,log=False)
    workflows = build_workflows(ontology, Graph(), intent_graph, pot_impls, log=False)
    t2 = time.perf_counter()
    #workflows = build_workflows_combinations(ontology, Graph(), 1.0, intent_graph,tcc, log=False)
    #t3 = time.perf_counter()

    t_comb = t2 - t1
    t_wkfw = t_comb

    #for i, w in enumerate(workflows[:10]):
    #    w.serialize(experiment_folder / f'Workflow{i}.ttl')

    return t_comb, t_wkfw, workflows#len(workflows)

def run_experiment_suite(source_folder: str, data_file: str, destination_folder: str):
    cboxes = [f for f in Path(source_folder).iterdir() if f.suffix == '.ttl']
    cboxes.sort(reverse=True)
    print(cboxes)
    regex = r'cbox_(\d+)_(\d+)i_(\d+)shi_(\d+)ish_(\d+)cpi.ttl'

    result_file = open(Path(destination_folder)/'results.csv', 'w')
    result_file.write('main_impls,prep_levels,i_shapes,cpi,time_comb, time_work, num_workflows\n')

    for cbox in tqdm(cboxes, desc='Experiments', position=2):
        experiment_folder = Path(destination_folder) / 'workflows' /  cbox.stem
        Path(experiment_folder).mkdir(exist_ok=True)

        data_file = Path(data_file).resolve()

        print(cbox)
        print(cbox.name)

        match = re.match(regex, cbox.name)
        m_impl = int(match.group(1))
        c_impl = int(match.group(2))
        sh_i = int(match.group(3))
        i_sh = int(match.group(4))
        cpi = int(match.group(5))

        tqdm.write(f'Running experiment for {m_impl}/{c_impl}/{sh_i}/{i_sh}/{cpi}')
        tqdm.write(f'\t# Components: {(m_impl + c_impl)*cpi}')
        tqdm.write(f'\t# Requirements per component: {i_sh}')
        tqdm.write(f'\t# Components per implementation: {cpi}')

        t_c, t_w, nw = run_experiment(Path(source_folder).resolve() / cbox.name , data_file, experiment_folder)
        tqdm.write(f'--------------------------------------------------------------------------------------------')

        result_file.write(f'{m_impl},{c_impl},{i_sh},{cpi},{t_c},{t_w},{nw}\n')

if __name__ == '__main__':
    run_experiment_suite('./fake_cboxes/generation_test', './annotated_datasets/titanic.ttl' ,'./results')