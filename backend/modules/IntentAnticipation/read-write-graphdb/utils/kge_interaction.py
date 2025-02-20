import os
import csv
import time
import pickle
import torch
import pandas as pd


from pykeen.triples import TriplesFactory
from pykeen.training import SLCWATrainingLoop
from torch.optim import Adam
from pykeen.models import TransE



def annotate_tsv(user,intent,dataset):
    #TODO : HOW ARE USER,INTENT,DATASET PASSED HERE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    new_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "new_triples.tsv")
    new_triples_path = os.path.normpath(new_path)


    experiment = user+intent+dataset + str(time.time()).split('.')[0]

    #TODO ADDAPT TO THE ONTOLOGY
    triples = [
    (user, 'specifies', experiment), 
    (experiment, 'hasIntent', intent),
    (experiment, 'hasDataset', dataset)]

    with open(new_triples_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerows(triples)
    
    return experiment # Is just experiment what we want?


def kge_recommendations(experiment):

    seed = 8182
    embedding_dimension = 128
    learning_rate_fine_tune = 0.0001
    num_finetune_epochs = 1
    num_negs_per_pos = 20

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "new_triples.tsv")
    new_triples_path = os.path.normpath(path)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
    triples_path = os.path.normpath(path)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    # LOAD ALL DICTIONARIES AND EMBEDDINGS

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_to_id.pkl")
    norm_path_e2i = os.path.normpath(path)
    with open(norm_path_e2i, "rb") as f:
        old_ent_to_id = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "relation_to_id.pkl")
    norm_path_r2i = os.path.normpath(path)
    with open(norm_path_r2i, "rb") as f:
        old_rel_to_id = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_representations.pkl")
    norm_path_ee = os.path.normpath(path)
    with open(norm_path_ee, "rb") as f:
        old_ent_emb = pickle.load(f).to(device)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "relation_representations.pkl")
    norm_path_re = os.path.normpath(path)
    with open(norm_path_re, "rb") as f:
        old_rel_emb = pickle.load(f).to(device)

    df1 = pd.read_csv(triples_path, sep="\t", header= None)
    df2 = pd.read_csv(new_triples_path, sep="\t", header=None)
    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df.to_csv(triples_path, sep="\t", index=False)

    training_triples_factory = TriplesFactory.from_path(triples_path)

    # Initialize the model with all the entities/relations
    model = TransE(triples_factory=training_triples_factory, embedding_dim=embedding_dimension, random_seed = seed).to(device)

    new_ent_emb = model.entity_representations[0](indices= None).clone().detach().to(device)
    new_rel_emb = model.relation_representations[0](indices= None).clone().detach().to(device)

    # Get new mappings

    new_ent_to_id = training_triples_factory.entity_to_id
    new_rel_to_id = training_triples_factory.relation_to_id

    # Keep the embeddings of old entities/relations
    with torch.no_grad():
        for i in old_ent_to_id:
            old_idx = old_ent_to_id[i]
            new_idx = training_triples_factory.entity_to_id[i]

            old_vector = old_ent_emb[old_idx].to(device)
            new_ent_emb[new_idx] = old_vector

        for j in old_rel_to_id:
            old_idx = old_rel_to_id[j]
            new_idx = training_triples_factory.relation_to_id[j]

            old_vector = old_rel_emb[old_idx].to(device)
            new_rel_emb[new_idx] = old_vector

        model.entity_representations[0]._embeddings.weight.copy_(new_ent_emb)
        model.relation_representations[0]._embeddings.weight.copy_(new_rel_emb)
    
    #TODO Initialization

    model = model.to(device)

    training_triples = TriplesFactory.from_path(new_triples_path, entity_to_id=new_ent_to_id, relation_to_id=new_rel_to_id)

    optimizer = Adam(params=model.get_grad_params(),lr=learning_rate_fine_tune)

    training_loop = SLCWATrainingLoop(model=model,
                                    triples_factory=training_triples,
                                    optimizer=optimizer,
                                    negative_sampler_kwargs = {'num_negs_per_pos':num_negs_per_pos})

    tl = training_loop.train(triples_factory=training_triples,
                            num_epochs=num_finetune_epochs)
    


    with open(norm_path_ee, "wb") as f:
        pickle.dump(model.entity_representations[0](indices= None).clone().detach(), f)

    with open(norm_path_re, "wb") as f:
        pickle.dump(model.relation_representations[0](indices= None).clone().detach(), f)

    with open(norm_path_e2i, "wb") as f:
        pickle.dump(new_ent_to_id, f)

    with open(norm_path_r2i, "wb") as f:
        pickle.dump(new_rel_to_id, f)
    

    # Predict

    #TODO Adapt to what we want to predict
    relations = ['http://localhost/7200/intentOntology#achieves','http://localhost/7200/intentOntology#hasConstraint']
    head = experiment

    head_idx = new_ent_to_id[head]
    relation_idxs = [new_rel_to_id[relation] for relation in relations]

    batch = []
    for relation_idx in relation_idxs:
        batch.append([head_idx,relation_idx])

    hr_batch = torch.tensor(batch, dtype=torch.long)

    tail_scores = model.predict_t(hr_batch)

    # Get the top-k predicted head entities
    k = 1
    top_k_tails = torch.topk(tail_scores, k=k)
    idx = top_k_tails.indices

    inv_map = {v: k for k, v in new_ent_to_id.items()}

    results = {'prediction1':inv_map[int(idx[0])], 'prediction2':inv_map[int(idx[1])]}


    return results




