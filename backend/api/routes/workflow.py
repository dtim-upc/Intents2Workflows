import json

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List, Union
from models import Workflow, Intent  # Assuming models are in a file named models.py
from database.database import SessionLocal  # Assuming database connection is defined in database.py
from pydantic import BaseModel

# Create the router for workflows
router = APIRouter()


# Pydantic models for validation
class WorkflowCreateRequest(BaseModel):
    workflowName: str
    visualRepresentation: List[List[Union[List[str], str]]]  # Matches the frontend's map structure
    stringGraph: str


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/intent/{intent_name}/workflow")
def create_workflow(request_session:Request, intent_name: str, request: WorkflowCreateRequest, db: Session = Depends(get_db)):

    session_id = request_session.state.session_id

    # Check if the intent exists
    intent = db.query(Intent).filter(Intent.name == intent_name, Intent.session_id==session_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Create the workflow instance
    new_workflow = Workflow(
        name=request.workflowName,
        visual_representation=str(json.dumps(request.visualRepresentation)),  # Convert dict to string for storing
        graph=request.stringGraph,
        intent_name=intent_name,
        session_id = session_id
    )

    # Add workflow to DB
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    # Associate the workflow with the intent
    intent.workflows.append(new_workflow)  # Assuming a relationship exists
    db.commit()

    return {"message": "Workflow added successfully", "workflow": new_workflow.to_dict()}

# Update a workflow
# @router.put("/{workflow_name}")
# def update_workflow(workflow_name: str, workflow: WorkflowUpdate, db: Session = Depends(get_db)):
#     db_workflow = db.query(Workflow).filter(Workflow.name == workflow_name).first()
#
#     if db_workflow is None:
#         raise HTTPException(status_code=404, detail="Workflow not found")
#
#     db_workflow.visual_representation = workflow.visual_representation
#     db_workflow.graph = workflow.graph
#     db.commit()
#     db.refresh(db_workflow)
#     return db_workflow


# Delete a workflow
@router.delete("/intent/{intent_name}/workflow/{workflow_name}")
def delete_workflow(request:Request, intent_name: str, workflow_name: str, db: Session = Depends(get_db)):
    session_id = request.state.session_id

    db_workflow = db.query(Workflow).filter(Workflow.name == workflow_name, Workflow.intent_name == intent_name, Workflow.session_id==session_id).first()

    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(db_workflow)
    db.commit()

    return {"message": "Workflow deleted"}
