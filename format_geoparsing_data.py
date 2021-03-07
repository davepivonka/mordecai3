import xmltodict
import numpy as np
from tqdm.autonotebook import tqdm
from spacy.tokens import DocBin
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q
import re

import elastic_utilities as util

import spacy
from spacy.language import Language
from spacy.tokens import Token, Doc
from spacy.pipeline import Pipe
import numpy as np
import jsonlines
from typing import List, Set, Dict, Tuple, Optional

import pickle



Token.set_extension('tensor', default=False)

@Language.component("token_tensors")
def token_tensors(doc):
    chunk_len = len(doc._.trf_data.tensors[0][0])
    token_tensors = [[]]*len(doc)
    
    for n, i in enumerate(doc):
        wordpiece_num = doc._.trf_data.align[n]
        for d in wordpiece_num.dataXd:
            which_chunk = int(np.floor(d[0] / chunk_len))
            which_token = d[0] % chunk_len
            ## You can uncomment this to see that spaCy tokens are being aligned with the correct 
            ## wordpieces.
            #wordpiece = doc._.trf_data.wordpieces.strings[which_chunk][which_token]
            #print(n, i, wordpiece)
            token_tensors[n] = token_tensors[n] + [doc._.trf_data.tensors[0][which_chunk][which_token]]
    for n, d in enumerate(doc):
        if token_tensors[n]:
            d._.set('tensor', np.mean(np.vstack(token_tensors[n]), axis=0))
        else:
            d._.set('tensor',  np.zeros(doc._.trf_data.tensors[0].shape[-1]))
    return doc


def read_file(fn):
    if re.search("xml", fn):
        with open(fn, "r") as f:
            xml = f.read()
            data = xmltodict.parse(xml)
    elif re.search("jsonl", fn):
        with jsonlines.open(fn, "r") as f:
            data = list(f.iter())
    else:
        raise NotImplementedError("Don't know how to handle this filetype")
    return data 

def doc_to_ex_expanded(doc):
    """
    Take in a spaCy doc with a custom ._.tensor attribute on each token and create a list
    of dictionaries with information on each place name entity.

    In the broader pipeline, this is called after nlp() and the results are passed to the 
    Elasticsearch step.

    Parameters
    ---------
    doc: spacy.Doc 
      Needs custom ._.tensor attribute.

    Returns
    -------
    data: list of dicts
    """
    data = []
    doc_tensor = np.max(np.vstack([i._.tensor for i in doc]), axis=0)
    loc_ents = [ent for ent in doc.ents if ent.label_ in ['GPE', 'LOC', 'EVENT_LOC', 'NORP']]
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC', 'EVENT_LOC']:
            tensor = np.mean(np.vstack([i._.tensor for i in ent]), axis=0)
            other_locs = [i for e in loc_ents for i in e if i not in ent]
            if other_locs:
                locs_tensor = np.max(np.vstack([i._.tensor for i in other_locs if i not in ent]), axis=0)
            else:
                locs_tensor = np.zeros(len(tensor))
            d = {"placename": ent.text,
                 "tensor": tensor,
                 "doc_tensor": doc_tensor,
                 "locs_tensor": locs_tensor,
                 "sent": ent.sent.text,
                "start_char": ent[0].idx,
                "end_char": ent[-1].idx + len(ent.text)}
            data.append(d)
    return data

def data_to_docs(data, source):
    """
    NLP the training data and save the docs to disk
    """
    print("NLPing docs...")
    doc_bin = DocBin(store_user_data=True)
    if source == "prodigy":
        for doc in tqdm(nlp.pipe([i['text'] for i in data]), total=len(data)):
            doc_bin.add(doc)
    else:
        for doc in tqdm(nlp.pipe([i['text'] for i in data['articles']['article']]), total=len(data['articles']['article'])):
            doc_bin.add(doc)
    fn = f"source_{source}.spacy"
    with open(fn, "wb") as f:
        doc_bin.to_disk(fn)
    print(f"Wrote NLPed docs out to {fn}")



def data_formatter_prodigy(docs, data):
    """
    Format a single example from the Prodigy training round into a format for training.
    (placename, BERT embedding, correct geonames id)
    
    Returns
    -------
    data: dict
      - placename 
      - tensor
      - correct geonames id
    """
    formatted = []
    doc_num = 0
    for doc, ex in tqdm(zip(docs, data)): 
        # Check if the example is good
        if ex['answer'] in ['reject', 'ignore']:
            continue
        # get the correct geonames ID
        if 'accept' not in ex.keys():
            continue
        correct_id = [i['text'] for i in ex['options'] if i['id'] == ex['accept'][0]][0]
        try:
            correct_id = re.findall(r"\d+$", correct_id)[0]
        except IndexError:
            # this means it's a None/other example. Drop those for now
            continue
        # get the tokens matching what the annotator saw
        places = [i for i in doc if i.idx >= ex['spans'][0]['start'] and i.idx + len(i) <= ex['spans'][0]['end']]
        placename = ''.join([i.text_with_ws for i in places])
        # get the tensor for those tokens
        if places:
            loc_ents = [ent for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
            tensor = np.mean(np.vstack([i._.tensor for i in places]), axis=0)
            doc_tensor = np.max(np.vstack([i._.tensor for i in doc]), axis=0)
            other_locs = [i for e in loc_ents for i in e if i not in places]
            if other_locs:
                locs_tensor = np.max(np.vstack([i._.tensor for i in other_locs]), axis=0)
            else:
                locs_tensor = np.zeros(len(tensor))
            d = {"placename": placename,
               "tensor": tensor,
                "locs_tensor": locs_tensor,
                "doc_tensor": doc_tensor,
               "correct_geonamesid": correct_id}
            formatted.append(d)
        doc_num += 1
    return formatted

def data_formatter(docs, data, source):
    """
    This is for the data provided by Gritta et al
    """
    formatted = []
    doc_num = 0
    for doc, ex in tqdm(zip(docs, data['articles']['article'])):
        doc_tensor = np.max(np.vstack([i._.tensor for i in doc]), axis=0)
        loc_ents = [ent for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        for n, topo in enumerate(ex['toponyms']['toponym']):
            #print(topo['phrase'])
            if source == "gwn" and 'geonamesID' not in topo.keys():
                continue
            if source == "gwn" and not topo['geonamesID']:
                continue
            try:
                place_tokens = [i for i in doc if i.idx >= int(topo['start']) and i.idx + len(i) <= int(topo['end'])]
                other_locs = [i for e in loc_ents for i in e if i not in place_tokens]
                if other_locs:
                    locs_tensor = np.max(np.vstack([i._.tensor for i in other_locs]), axis=0)
                else:
                    locs_tensor = np.zeros(len(tensor))
                # remove NORPs?
                gpes = [i for i in place_tokens if i.ent_type_ in ['GPE', 'LOC']]
                if not gpes:
                    continue
                tensor = np.mean(np.vstack([i._.tensor for i in place_tokens]), axis=0)
                if source == "gwn":
                    correct_geonamesid = topo['geonamesID']
                    placename = topo['extractedName']
                else:
                    correct_geonamesid = topo['gaztag']['@geonameid']
                    placename = topo['phrase']

                formatted.append({"placename": placename,
                                  "tensor": tensor,
                                  "locs_tensor": locs_tensor,
                                  "doc_tensor": doc_tensor,
                                  "correct_geonamesid": correct_geonamesid})
            except Exception as e:
                pass
                #print(e)
                #print(f"{doc_num}_{n}")
        doc_num += 1
    return formatted

def format_source(source, conn):
    fn = f"source_{source}.pkl"
    print(f"reading in {source}...")
    # did it two different ways...
    try:
        with open(fn, "rb") as f:
            doc_bin = pickle.load(f)

    except FileNotFoundError:
        fn = f"source_{source}.spacy"
        with open(fn, "rb") as f:
            doc_bin = DocBin().from_disk(fn)
    print(f"Converting back to spaCy docs...")

    docs = list(doc_bin.get_docs(nlp.vocab))
    data = read_file(sources[source])

    if source == "prodigy":
        formatted = data_formatter_prodigy(docs, data)
    else:
        formatted = data_formatter(docs, data, source)
    esed_data = []
    for ex in tqdm(formatted):
        d = util.add_es_data(ex, conn)
        esed_data.append(d)
    print(f"Total place names in {source}: {len(esed_data)}")
    fn = f"es_formatted_{source}.pkl"
    print(f"Writing to {fn}...")
    with open(fn, 'wb') as f:
        pickle.dump(esed_data, f)


if __name__ == "__main__":
    print("Loading NLP stuff...")
    conn = util.make_conn()
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe("token_tensors")
    sources = {"tr":"Pragmatic-Guide-to-Geoparsing-Evaluation/data/Corpora/TR-News.xml",
              "lgl":"Pragmatic-Guide-to-Geoparsing-Evaluation/data/corpora/lgl.xml",
              "gwn": "Pragmatic-Guide-to-Geoparsing-Evaluation/data/GWN.xml",
              "prodigy": "../geo_annotated/loc_rank_db.jsonl"}

    #print("Reading in data...")
    #data = read_file(sources['prodigy'])
    #data_to_docs(data, "prodigy")

    for source in sources.keys():            
        format_source(source, conn)
    print("Complete")
