import io
from typing import Tuple
from fastapi import APIRouter, Form, Response, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from rdflib import RDF, Graph, Namespace, URIRef
from sqlalchemy.orm import Session
import os
from pathlib import Path
import time
import shutil
from urllib.parse import quote

from database.database import SessionLocal
from dataset_annotator import annotator, namespaces
from utils import tensor_preprocesser
from models import DataProduct

router = APIRouter()

MAX_FILENAME_LENGTH = 50
UPLOAD_DIR = "datasets"
ANNOTATOR_DIR = "annotated_datasets"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ANNOTATOR_DIR, exist_ok=True)

dmop = Namespace('http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#')
ab = Namespace('https://extremexp.eu/ontology/abox#')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_folder_hierarchy(path:Path):
    if path != Path(UPLOAD_DIR):
        if path.parent != Path(UPLOAD_DIR):
            create_folder_hierarchy(path.parent)
        path.mkdir(exist_ok=True)

def get_root_folder(folder_path:Path) -> Path:
    if folder_path.parent == Path(UPLOAD_DIR):
        return folder_path
    else:
        return get_root_folder(folder_path.parent)
    
def format_path(raw_path:str) ->Path:
    bound = int(MAX_FILENAME_LENGTH/2)
    parts = Path(raw_path).parts
    newparts = []
    for part in parts:
        qpart = quote(part)
        if len(qpart) > MAX_FILENAME_LENGTH:
            qpart = qpart[:bound] + "..." + qpart[-bound:]
        newparts.append(qpart)
    return Path(*newparts)

def process_file(file: UploadFile, session: str)->Tuple[str,int,float, Path]:
    session_path = Path(UPLOAD_DIR).joinpath(session)
    session_path.mkdir(exist_ok=True)

    file_path = session_path.joinpath(format_path(file.filename))
    print(file_path)

    # Save file
    create_folder_hierarchy(file_path.parent)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size = file_path.stat().st_size / (1024 * 1024)  # Convert to MB
    upload_file = file_path.stat().st_ctime

    return file.filename, size, upload_file, file_path

def get_potential_targets(dataset_node:URIRef, annotated_dataset:Graph):
    dataset_type = next(annotated_dataset.objects(dataset_node, RDF.type, unique=True))
    if dataset_type == dmop.TensorDataset:
        pot_targets = annotated_dataset.objects(dataset_node,namespaces.dmop.hasArray,unique=False)
    elif dataset_type == dmop.TabularDataset:
        pot_targets = annotated_dataset.objects(dataset_node,namespaces.dmop.hasColumn,unique=False)
    else:
        return []
    return [target.fragment for target in pot_targets]

def create_data_product(db: Session, session_id, filename, size, upload_time, file_path:Path, source_path:str)-> DataProduct:

    dataset_node, annotations = annotator.annotate_dataset(file_path,local_path=source_path)
    annotation_name = file_path.with_suffix('.ttl').name
    session_path = Path(ANNOTATOR_DIR).joinpath(session_id)
    session_path.mkdir(exist_ok=True)
    save_path = session_path.joinpath(f"{annotation_name}")
    pot_targets = get_potential_targets(dataset_node,annotations)

    annotations.serialize(save_path,format="turtle")

    data_product = DataProduct(
        name=quote(filename),
        creation_date=time.ctime(upload_time),
        size=round(size, 2),
        path=file_path.resolve().as_posix(),
        annotation_path=save_path.resolve().as_posix(),
        targets=",".join(pot_targets),  # Store as CSV string
        session_id=session_id
    )

    db.add(data_product)
    db.commit()

    return data_product

def get_annotation_path(db: Session,dp: DataProduct, session_id) -> str:
    data_product_formatted = quote(dp)
    data_product = db.query(DataProduct).filter(DataProduct.name == data_product_formatted, DataProduct.session_id == session_id).first()

    return data_product.annotation_path
    

def load_graph(path:str)->Graph:

    g = Graph()
    g.bind('dmop', dmop)
    g.parse(path, format="turtle")
    return g

def label_query(label, reset):
    query = f""" 
    PREFIX dmop: <{dmop}>

    DELETE {{
	    ?column dmop:isFeature ?c .
        ?column dmop:isLabel ?d .   
    }}
    INSERT {{
        ?column dmop:isFeature {'True' if reset else 'False'} .
        ?column dmop:isLabel {'False' if reset else 'True'} .
    }}
    WHERE {{
        ?column a dmop:Column .
        ?column dmop:isFeature ?c .
        ?column dmop:isLabel ?d .   
        FILTER(?column {'!=' if reset else '='} ab:{label})
    }}
    """

    return query


def add_label(graph:Graph, label:str) -> Graph:
    reset_query = label_query(label, reset=True)
    add_label_query = label_query(label, reset=False)
    graph.update(reset_query)
    graph.update(add_label_query)

    return graph

def get_dataset_uri(annotation_graph:Graph):
    uri = next(annotation_graph.subjects(RDF.type, dmop.TabularDataset, unique=True), "")
    if uri == "":
        uri = next(annotation_graph.subjects(RDF.type, dmop.TensorDataset, unique=True), "")
    return uri



@router.post("/data-products")
async def upload_file(request: Request, files: list[UploadFile] = File(...), tensor=Form(default="false"), original_path = Form(default=None), db: Session = Depends(get_db)):
    """Uploads a CSV file and saves metadata to the database."""
    #if not file.filename.endswith(".csv"):
        #raise HTTPException(status_code=400, detail="Only CSV files are allowed!")
    
    session_id = request.state.session_id

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if tensor == "true": #tensor import
        name, size, upload_time, path = process_file(files[0], session_id)
        file = tensor_preprocesser.get_npz(path)
        name, size, upload_time, path = process_file(UploadFile(file, size=len(file.getbuffer()), filename=name+".npz"), session_id)

        dp = create_data_product(db, name, size, upload_time, path, original_path, session_id)

        return JSONResponse(status_code=200, content={
        "message": "File uploaded successfully",
        "data_product": [dp.to_dict()]
    })



    folder = Path(files[0].filename).parent
    print(folder, Path(UPLOAD_DIR))

    dps = []

    if folder != Path('.'): #folder import
        folder_size = 0
        for file in files:
            _, size, upload_time , file_path = process_file(file, session_id)
            folder_size += size

        folder_path = get_root_folder(file_path)

        dp = create_data_product(db, session_id, folder_path.name, folder_size, upload_time,folder_path,original_path)
        dps.append(dp)

    else: #file import
        for file in files:
            name, size, upload_time, path = process_file(file, session_id)

            dp = create_data_product(db, session_id, name, size, upload_time, path, original_path)
            dps.append(dp)

    return JSONResponse(status_code=200, content={
        "message": "File uploaded successfully",
        "data_product": [data_product.to_dict() for data_product in dps]
    })

@router.get("/data-products")
async def list_uploaded_files(request: Request, db: Session = Depends(get_db)):
    """Returns a list of all stored CSV files."""

    session_id = request.state.session_id
    data_products = db.query(DataProduct).filter_by(session_id=session_id).all()
    return JSONResponse(status_code=200, content={"files": [dp.to_dict() for dp in data_products]})

@router.get("/data-products/{data_product}")
async def  get_data_product(request: Request, data_product:str, db: Session = Depends(get_db)):

    session_id = request.state.session_id

    annotation_path = get_annotation_path(db,data_product, session_id)
    annotation_graph = load_graph(annotation_path)
    serialized_graph = annotation_graph.serialize(format='ttl')
    
    return Response(content=serialized_graph, media_type="text/turtle")


@router.post("/data-products/{data_product}/annotations")
async def get_annotations(request: Request, data_product:str, label: str = Form(...), db: Session = Depends(get_db)):
    """Get dataset annotations and add labels"""

    session_id = request.state.session_id

    annotation_path = get_annotation_path(db,data_product, session_id)
    annotation_graph = load_graph(annotation_path)
    datasetURI = get_dataset_uri(annotation_graph)

    if label != "":
        updated_graph = add_label(annotation_graph,label)
    else:
        updated_graph = annotation_graph
    

    return JSONResponse(status_code=200, content={"annotations": updated_graph.serialize(), "datasetURI": datasetURI})





@router.delete("/data-products/{data_product}")
async def delete_data_product(request:Request, data_product: str, db: Session = Depends(get_db)):
    """Deletes a data product by its name from the database and file system."""

    session_id = request.state.session_id

    data_product_formatted = quote(data_product)
    data_product = db.query(DataProduct).filter(DataProduct.name == data_product_formatted, DataProduct.session_id==session_id).first()

    if data_product is None:
        raise HTTPException(status_code=404, detail="Data product not found")

    # Delete file from the file system
    if Path(data_product.path).is_dir():
        shutil.rmtree(data_product.path)
    else:
        Path(data_product.path).unlink()
    
    # Delete annotation file from the file system
    Path(data_product.annotation_path).unlink()

    # Delete data product from the database
    db.delete(data_product)
    db.commit()

    return JSONResponse(status_code=200, content={"message": f"Data product '{data_product}' deleted successfully"})


#################################################################### DDM integration #########################################################################################
import json
import requests

BASE_DIR = Path(__file__).resolve().parent
cred_path = BASE_DIR / "DDM_credentials.json"

with cred_path.open() as f:
    creds = json.load(f)

USERNAME = creds["username"]
PASSWORD = creds["password"]


class DDMClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.username = USERNAME
        self.password = PASSWORD
        self._token = None
    
    @property
    def token(self):
        if self._token is None:
            self.login()
        return self._token


    def login(self):
        self._token = None

        login_body = {
            "username": self.username,
            "password": self.password,
        }

        print(login_body)

        try:
            # Making the POST request
            response = requests.post(f"{self.base_url}/person/login", json=login_body)
        
        except Exception as e:
            print("Option explorer connection error:", e)
            return



        # Check the response
        if response.status_code == 200:
            response_json = response.json()
            print("RESPONSE",response_json)
            self._token = response_json.get("access_token",None)
        else:
            print("ERROR getting token:",response.text)
            
        return
    
ddm = DDMClient("https://ddm.extremexp-icom.intracom-telecom.com/extreme_auth/api/v1/")
    
@router.get("/ddm")
async def  get_ddm_token():
    return {"token": ddm.token}