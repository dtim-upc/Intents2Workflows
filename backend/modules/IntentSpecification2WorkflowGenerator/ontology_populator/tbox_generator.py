import sys
import os
from typing import List, Union

from rdflib.collection import Collection

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import *


def add_class(graph, nodes):
    l = nodes if isinstance(nodes, list) else [nodes]
    for node in l:
        graph.add((node, RDF.type, OWL.Class))


def add_union(graph, nodes):
    sequence = Collection(graph, BNode(), nodes)
    union = BNode()
    graph.add((union, OWL.unionOf, sequence.uri))
    return union


def add_object_property(graph, property, domain, range):
    graph.add((property, RDF.type, OWL.ObjectProperty))
    if domain:
        graph.add((property, RDFS.domain, add_union(graph, domain) if isinstance(domain, list) else domain))
    if range:
        graph.add((property, RDFS.range, add_union(graph, range) if isinstance(range, list) else range))


def add_datatype_property(graph, property, domain, range):
    if isinstance(range, list):
        for r in range:
            assert r in XSD
    else:
        assert range in XSD
    graph.add((property, RDF.type, OWL.DatatypeProperty))
    if domain:
        graph.add((property, RDFS.domain, add_union(graph, domain) if isinstance(domain, list) else domain))
    if range:
        graph.add((property, RDFS.range, add_union(graph, range) if isinstance(range, list) else range))


def add_property(graph, property, domain, range):
    graph.add((property, RDF.type, RDF.Property))
    if domain:
        graph.add((property, RDFS.domain, add_union(graph, domain) if isinstance(domain, list) else domain))
    if range:
        graph.add((property, RDFS.range, add_union(graph, range) if isinstance(range, list) else range))


def init_ontology() -> Graph:
    ontology = get_graph_xp()

    ontology.add((URIRef(str(tb)), RDF.type, OWL.Ontology))
    ontology.add((URIRef(str(tb)), RDFS.label, Literal("ExtremeXP Ontology TBox")))
    return ontology


def add_classes(ontology: Graph):
    classes = [
        tb.User,
        tb.Intent,
        tb.Requirement,
        tb.EvaluationRequirement,
        tb.Method,
        tb.Metric,
        tb.VisualizationRequirement,
        tb.PlotType,
        tb.PlotProperties,
        tb.ExperimentConstraint,
        tb.ConstraintValue,
        tb.RangeValue,
        tb.LiteralValue,
        tb.Task,
        tb.Algorithm,
        tb.Implementation,
        tb.LearnerImplementation,
        tb.ApplierImplementation,
        tb.VisualizerImplementation,
        tb.DataTag,
        tb.Parameter,
        tb.ParameterSpecification,
        tb.ParameterValue,
        tb.Component,
        tb.LearnerComponent,
        tb.ApplierComponent,
        tb.VisualizerComponent,
        tb.Transformation,
        tb.CopyTransformation,
        tb.LoaderTransformation,
        tb.Workflow,
        tb.WorkflowCharacteristics,
        tb.UserFeedback,
        tb.Step,
        tb.ModelEvaluation,
        tb.Data,
        tb.Dataset,
        tb.Model,
        tb.DataCharacteristics,
        tb.DataSpec,
        tb.DataSpecTag,
        tb.Rule,
        tb.AlgebraicExpression,
        tb.Operation,
        tb.FactorParameter,
        tb.NumericParameter,
        tb.BaseParameter,
        tb.DerivedParameter,
        tb.FactorLevel,
        tb.Engine,
        tb.EngineImplementation,
        tb.EngineParameter,
    ]
    add_class(ontology, classes)

    ontology.add((tb.CopyTransformation, RDFS.subClassOf, tb.Transformation))
    ontology.add((tb.LoaderTransformation, RDFS.subClassOf, tb.Transformation))

    ontology.add((tb.LearnerImplementation, RDFS.subClassOf, tb.Implementation))
    ontology.add((tb.ApplierImplementation, RDFS.subClassOf, tb.Implementation))
    ontology.add((tb.VisualizerImplementation, RDFS.subClassOf, tb.Implementation))
    ontology.add((tb.LearnerImplementation, OWL.disjointWith, tb.ApplierImplementation))
    ontology.add((tb.VisualizerImplementation, OWL.disjointWith, tb.ApplierImplementation))
    ontology.add((tb.VisualizerImplementation, OWL.disjointWith, tb.LearnerImplementation))

    ontology.add((tb.LearnerComponent, RDFS.subClassOf, tb.Component))
    ontology.add((tb.ApplierComponent, RDFS.subClassOf, tb.Component))
    ontology.add((tb.VisualizerComponent, RDFS.subClassOf, tb.Component))
    ontology.add((tb.LearnerComponent, OWL.disjointWith, tb.ApplierComponent))
    ontology.add((tb.VisualizerComponent, OWL.disjointWith, tb.ApplierComponent))
    ontology.add((tb.VisualizerComponent, OWL.disjointWith, tb.LearnerComponent))

    ontology.add((tb.RangeValue, RDFS.subClassOf, tb.ConstraintValue))
    ontology.add((tb.LiteralValue, RDFS.subClassOf, tb.ConstraintValue))

    ontology.add((tb.Model, RDFS.subClassOf, tb.Data))
    ontology.add((tb.Dataset, RDFS.subClassOf, tb.Data))
    ontology.add((dmop.TabularDataset, RDFS.subClassOf, tb.Dataset))
    ontology.add((dmop.TensorDataset, RDFS.subClassOf, tb.Dataset))

    ontology.add((tb.FactorParameter, RDFS.subClassOf, tb.Parameter))
    ontology.add((tb.NumericParameter, RDFS.subClassOf, tb.Parameter))
    ontology.add((tb.BaseParameter, RDFS.subClassOf, tb.Parameter))
    ontology.add((tb.DerivedParameter, RDFS.subClassOf, tb.Parameter))
    ontology.add((tb.FactorParameter, OWL.disjointWith, tb.NumericParameter))
    ontology.add((tb.BaseParameter, OWL.disjointWith, tb.DerivedParameter))

    ontology.add((tb.EngineParameter, RDFS.subClassOf, tb.Parameter))

def add_properties(ontology: Graph):
    properties = [
        #User
        (tb.defines, tb.User, tb.Intent),
        # Intent
        (tb.overData, tb.Intent, tb.Data),
        (tb.specifies, tb.Intent, tb.Algorithm),
        (tb.specifiesValue, tb.Intent, tb.ParameterValue),
        (tb.hasConstraint, tb.Intent, tb.Constraint),
        (tb.hasRequirement, tb.Intent, tb.Requirement),
        (tb.has_component_threshold, tb.Intent, XSD.double),
        (tb.has_complexity, tb.Intent, XSD.unsignedInt),
        # ParameterValue
        (tb.forParameter, tb.ParameterValue, tb.Parameter),
        # Requirement
        (tb.hasEvaluationRequirement, tb.Requirement, tb.EvaluationRequirement),
        (tb.hasVisualizationRequirement, tb.Requirement, tb.VisualizationRequirement),
        # Evaluation Requirement
        (tb.withMethod, tb.EvaluationRequirement, tb.Method),
        (tb.onMetric, tb.EvaluationRequirement, tb.Metric),
        # Task
        (tb.subtaskOf, tb.Task, tb.Task),
        (tb.tackles, tb.Task, tb.Intent),
        # Workflow
        (tb.generatedFor, tb.Workflow, tb.Intent),
        (tb.hasEvaluation, tb.Workflow, tb.ModelEvaluation),
        (tb.hasFeedback, tb.Workflow, tb.UserFeedback),
        (dolce.hasQuality, tb.Workflow, tb.WorkflowCharacterisitics),
        (tb.hasStep, tb.Workflow, tb.Step),
        (tb.hasComponent, tb.Workflow, tb.Component),
        # Workflow Characteristics
        ### TO BE DEFINED
        # Model Evaluatoin
        (tb.specifiesMetric, tb.ModelEvaluation, tb.Metric),
        (tb.hasValue, tb.ModelEvaluation, XSD.double),
        # Constraint
        (tb.constrainedBy, tb.Intent, tb.ExperimentConstraint),
        (tb.isHard, tb.ExperimentConstraint, XSD.boolean),
        (tb.constraintType, tb.ExperimentConstraint, XSD.string),
        ### tb.on is TO BE DEFINED
        # Constraint Value
        (tb.hasConstraintValue, tb.ExperimentConstraint, tb.ConstraintValue),
        (tb.hasOptionExplorerName, tb.ExperimentConstraint, XSD.string),
        (tb.hasMinValue, tb.RangeValue, XSD.double),
        (tb.hasMaxValue, tb.RangeValue, XSD.double),
        (tb.hasLiteralValue, tb.LiteralValue, XSD.string),
        ### tb.hasValue is TO BE DEFINED
        # Algorithm
        (tb.solves, tb.Algorithm, tb.Task),
        # Implementation
        (tb.implements, tb.Implementation, tb.Algorithm),
        (tb.hasParameter, tb.Implementation, tb.Parameter),
        (tb.hasLearner, tb.ApplierImplementation, tb.LearnerImplementation),
        (tb.hasApplier, tb.LearnerImplementation, tb.ApplierImplementation),
        (tb.hasVisualizer, tb.LearnerImplementation, tb.VisualizerImplementation),
        (tb.hasLearner, tb.VisualizerImplementation, tb.LearnerImplementation),
        (tb.specifiesInput, tb.Implementation, tb.DataSpec),
        (tb.specifiesOutput, tb.Implementation, tb.DataSpec),
        (tb.has_engine, tb.EngineImplementation, tb.Engine),
        (tb.compatibleWith, tb.Implementation, tb.Engine),
        # Engine Implementation
        #TODO: to be defined
        # Component
        (tb.hasTransformation, tb.Component, RDF.List),
        (tb.hasImplementation, tb.Component, tb.Implementation),
        (tb.overridesParameter, tb.Component, tb.ParameterSpecification),
        (tb.exposesParameter, tb.Component, tb.Parameter),
        (tb.hasLearner, tb.ApplierComponent, tb.LearnerComponent),
        (tb.hasApplier, tb.LearnerComponent, tb.ApplierComponent),
        (tb.hasVisualizer, tb.LearnerComponent, tb.VisualizerComponent),
        (tb.hasLearner, tb.VisualizerComponent, tb.LearnerComponent),
        (tb.hasRule, tb.Component, tb.Rule),
        # Step
        (tb.followedBy, tb.Step, tb.Step),
        (tb.hasInput, tb.Step, tb.Data),
        (tb.hasOutput, tb.Step, tb.Data),
        (tb.runs, tb.Step, tb.Component),
        (tb.usesParameter, tb.Step, tb.Parameter),
        # Parameter
        (tb.specifiedBy, tb.BaseParameter, tb.ParameterSpecification),
        (tb.has_datatype, tb.Parameter, None),
        (tb.has_defaultvalue, tb.Parameter, None),

        (tb.hasLevel, tb.FactorParameter, tb.FactorLevel),
        (tb.derivedFrom, tb.DerivedParameter, tb.AlgebraicExpression),

        #Algebraic Operation
        #(tb.hasTerm1, tb.AlgebraicExpression, tb.Parameter),
        #(tb.hasTerm1, tb.AlgebraicExpression, tb.AlgebraicOperation),
        #(tb.hasTerm1, tb.AlgebraicExpression, XSD.numeric),
        #(tb.hasTerm2, tb.AlgebraicExpression, tb.Parameter),
        #(tb.hasTerm2, tb.AlgebraicExpression, tb.AlgebraicOperation),
        #(tb.hasTerm2, tb.AlgebraicExpression, XSD.numeric),
        (tb.hasOperation, tb.AlgebraicExpression, tb.Operation),

        #Engine parameter
        #TODO: to be defined

        # Hyperparameter Specification
        (tb.hasValue, tb.ParameterSpecification, None),
        # Data
        (dolce.hasQuality, tb.Data, tb.DataCharacteristics),
        # Data Characteristics
        (tb.hasValue, tb.DataCharacteristics, XSD.string),
        # DataSpec
        (tb.hasSpecTag, tb.DataSpec, tb.DataSpecTag),
        # DataSpecTag
        (tb.hasDatatag, tb.DataSpecTag, tb.DataTag),
        (tb.hasImportanceLevel, tb.DataSpecTag, XSD.unsignedInt),
        # Rule
        (tb.relatedtoTask, tb.Rule, tb.Task),
        (tb.relatedtoDatatag, tb.Rule, tb.Datatag),
    ]
    for s, p, o in properties:
        add_object_property(ontology, s, p, o)

    ontology.add((tb.subtaskOf, RDF.type, OWL.TransitiveProperty))

    dproperties = [
        # Transformation
        (tb.copy_input, tb.CopyTransformation, XSD.integer),
        (tb.copy_output, tb.CopyTransformation, XSD.integer),
        (tb.transformation_language, tb.Transformation, XSD.string),
        (tb.transformation_query, tb.Transformation, XSD.string),
        # Data
        (tb.has_position, [tb.Data, tb.DataSpec, tb.Step, tb.Parameter], XSD.integer),
        (tb.has_condition, tb.Parameter, XSD.string)
    ]

    for s, p, o in dproperties:
        add_datatype_property(ontology, s, p, o)

    subproperties = [
        # Column
        (dmop.hasColumnName, dmop.ColumnInfoProperty),
        (dmop.hasDataPrimitiveTypeColumn, dmop.ColumnInfoProperty),
        (dmop.hasPosition, dmop.ColumnInfoProperty),
        (dmop.isCategorical, dmop.ColumnInfoProperty),
        (dmop.isFeature, dmop.ColumnInfoProperty),
        (dmop.isLabel, dmop.ColumnInfoProperty),
        (dmop.isUnique, dmop.ColumnInfoProperty),
        (dmop.containsNulls, dmop.ColumnValueInfoProperty),
        (dmop.hasMeanValue, dmop.ColumnValueInfoProperty),
        (dmop.hasStandardDeviation, dmop.ColumnValueInfoProperty),
        (dmop.hasMaxValue, dmop.ColumnValueInfoProperty),
        (dmop.hasMinValue, dmop.ColumnValueInfoProperty),
        (dmop.isNormalDistribution, dmop.ColumnInfoProperty),
        (dmop.hasOutliers, dmop.ColumnInfoProperty),

        # Dataset
        (dmop.delimiter, dmop.DatasetPhysicalProperty),
        (dmop.doubleQuote, dmop.DatasetPhysicalProperty),
        (dmop.encoding, dmop.DatasetPhysicalProperty),
        (dmop.fileFormat, dmop.DatasetPhysicalProperty),
        (dmop.hasHeader, dmop.DatasetPhysicalProperty),
        (dmop.isNormalized, dmop.DatasetValueInfoProperty),
        (dmop.lineDelimiter, dmop.DatasetPhysicalProperty),
        (dmop.numberOfColumns, dmop.DatasetInfoProperty),
        (dmop.numberOfRows, dmop.DatasetInfoProperty),
        (dmop.path, dmop.DatasetPhysicalProperty),
        (dmop.quoteChar, dmop.DatasetPhysicalProperty),
        (dmop.skipInitialSpace, dmop.DatasetPhysicalProperty),
        (dmop.isTrainDataset, dmop.DatasetInfoProperty),
        (dmop.isTestDataset, dmop.DatasetInfoProperty),
        (dmop.isNormallyDistributed, dmop.DatasetInfoProperty),
        (dmop.containsOutliers, dmop.DatasetInfoProperty),
    ]

    for s, o in subproperties:
        ontology.add((s, RDFS.subPropertyOf, o))


def main(dest: str = '../ontologies/tbox.ttl') -> None:
    ontology = init_ontology()
    add_classes(ontology)
    add_properties(ontology)
    ontology.serialize(dest, format='turtle')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
