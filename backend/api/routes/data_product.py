from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import time
import csv
import shutil
from database.database import SessionLocal, init_db
from models import DataProduct

router = APIRouter()

UPLOAD_DIR = "datasets"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/data-product")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads a CSV file and saves metadata to the database."""
    #if not file.filename.endswith(".csv"):
        #raise HTTPException(status_code=400, detail="Only CSV files are allowed!")
    
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))  # Global path

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
    upload_time = time.ctime(os.path.getctime(file_path))

    if file.filename.endswith(".csv"):# Extract CSV headers
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            attributes = next(reader, [])
    else:
        attributes = []

    # Save to database
    data_product = DataProduct(
        name=file.filename,
        creation_date=upload_time,
        size=round(file_size, 2),
        path=file_path,
        attributes=",".join(attributes)  # Store as CSV string
    )

    db.add(data_product)
    db.commit()

    return JSONResponse(status_code=200, content={
        "message": "File uploaded successfully",
        "data_product": data_product.to_dict()
    })

@router.get("/data-products")
async def list_uploaded_files(db: Session = Depends(get_db)):
    """Returns a list of all stored CSV files."""
    data_products = db.query(DataProduct).all()
    return JSONResponse(status_code=200, content={"files": [dp.to_dict() for dp in data_products]})


@router.delete("/data-product/{data_product}")
async def delete_data_product(data_product: str, db: Session = Depends(get_db)):
    """Deletes a data product by its name from the database and file system."""
    data_product = db.query(DataProduct).filter(DataProduct.name == data_product).first()

    if data_product is None:
        raise HTTPException(status_code=404, detail="Data product not found")

    # Delete file from the file system
    if os.path.exists(data_product.path):
        os.remove(data_product.path)

    # Delete data product from the database
    db.delete(data_product)
    db.commit()

    return JSONResponse(status_code=200, content={"message": f"Data product '{data_product}' deleted successfully"})
