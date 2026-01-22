import json

from sqlalchemy import Column, String, Float, Text, ForeignKey, PrimaryKeyConstraint, Date, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database.database import Base


# New Workflow Class
class Workflow(Base):
    __tablename__ = "workflows"

    name = Column(String)
    visual_representation = Column(Text, nullable=False)  # Map as string representation
    graph = Column(String, nullable=False)
    session_id = Column(String)
    intent_name = Column(String)  # Foreign key to Intent

    # Define composite primary key
    __table_args__ = (PrimaryKeyConstraint('name', 'intent_name', 'session_id'),
                      ForeignKeyConstraint(
                    ['intent_name', 'session_id'],  
                    ['intents.name', 'intents.session_id']  
        ),)

    intent = relationship("Intent", back_populates="workflows")

    def to_dict(self):
        return {
            "name": self.name,
            "visual_representation": json.loads(self.visual_representation) if self.visual_representation else {},  # Convert string to dictionary
            "graph": self.graph
        }


# Updated Intent Class
class Intent(Base):
    __tablename__ = "intents"

    name = Column(String, primary_key=True, index=True)
    session_id = Column(String, primary_key=True)
    problem = Column(Text, nullable=False)
    data_product_name = Column(String)

    __table_args__ = (ForeignKeyConstraint(
                    ['data_product_name', 'session_id'],  
                    ['data_products.name', 'data_products.session_id']  
        ),)



    data_product = relationship("DataProduct")
    workflows = relationship("Workflow", back_populates="intent", lazy="dynamic", cascade="all, delete")

    def to_dict(self):
        return {
            "name": self.name,
            "problem": self.problem,
            "data_product": self.data_product.to_dict() if self.data_product else None,
            "workflows": [workflow.to_dict() for workflow in self.workflows]  # Convert back to list of workflows
        }


class DataProduct(Base):
    __tablename__ = "data_products"

    name = Column(String, primary_key=True)  # Filename and session as primary key
    session_id = Column(String, primary_key=True)
    creation_date = Column(String, nullable=False)
    size = Column(Float, nullable=False)
    path = Column(String, nullable=False)
    targets = Column(Text, nullable=False)  # Stored as comma-separated values
    annotation_path = Column(String, nullable=False)

    intents = relationship("Intent", back_populates="data_product", lazy="dynamic", cascade="all, delete")

    def to_dict(self):
        return {
            "name": self.name,
            "creation_date": self.creation_date,
            "size": self.size,
            "path": self.path,
            "targets": self.targets.split(","),  # Convert back to list
            "annotation_path": self.annotation_path,
        }
