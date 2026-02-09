
import { Icon, UI, Button } from '@site/src/components/UI'
import { StepList } from '@site/src/components/StepList'
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'
import Admonition from '@theme/Admonition'
import CodeBlock from '@theme/CodeBlock';

import WeRDFImg from '@site/static/img/WE-RDF.png'
import WeKNIMEImg from '@site/static/img/WE-KNIME.png'
import WePythonImg from '@site/static/img/WE-Python.png'
import WeXXPImg from '@site/static/img/WE-XXP.png'
import WeImg from '@site/static/img/WE.png'
import DSL from '@site/static/img/DSL.png'

# Workflow Exporter
Workflow exporter allows the user to export the analytical pipelines materialized in the workflow planner in different formats.

<Zoom>
<img
    src={WeImg}
    alt="Workflow Exporter"
    style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
    className="zoomable"
/>
</Zoom>



## Export to RDF
<StepList
  steps={[
    { content: (
        <>
        Select a workflow and click the corresponding  <Button icon="download" iconSize="24px">RDF</Button> button. 
        <br/><br/>
        Alternatively, If you want to export all the workflows, click <Button extra_class="select-button">DOWNLOAD ALL RDF REPRESENTATIONS</Button> to get a <b>ZIP</b> file with all them.
        <Zoom>
        <img
            src={WeRDFImg}
            alt="Translate to RDF"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    }
  ]}
/>

The exported file will have this structure:

<div className="codeBlockWithTitle">
  <div className="codeBlockTitle">Xgboost Dart 0.ttl</div>

  ```js
  export default {
@prefix ab: <https://extremexp.eu/ontology/abox#> .
@prefix cb: <https://extremexp.eu/ontology/cbox#> .
@prefix dmop: <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix tb: <https://extremexp.eu/ontology/tbox#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632 a tb:Workflow ;
    tb:compatibleWith cb:KNIME,
        cb:Python ;
    tb:generatedFor ab:I2Cat ;
    tb:hasStep ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_0_implementation_data_reader,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_2_implementation_numerical_projection,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_3_implementation_xgboost_learner,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_4_implementation_numeric_projection_predictor,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_5_implementation_xgboost_predictor,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_6_implementation_data_writer .

cb:Classification tb:tackles ab:I2Cat .

ab:implementation-data_partitioning-count_\(absolute_size\)_workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning_specification a tb:ParameterSpecification ;
    tb:hasValue 10 .

ab:implementation-data_partitioning-fraction_\(relative_size\)_workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning_specification a tb:ParameterSpecification ;
    tb:hasValue 2.5e-01 .

ab:I2Cat a tb:Intent ;
    tb:hasConstraint cb:accuracy,
        cb:ram ;
    tb:has_complexity 1 ;
    tb:has_component_threshold 1e+00 ;
    tb:overData ab:T1003.001_%2520OS%2520Credent...024-09-13_dataset .

ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning a tb:Step ;
    tb:followedBy ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_2_implementation_numerical_projection,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_4_implementation_numeric_projection_predictor ;
    tb:hasInput [ a tb:Data ;
            tb:has_data ab:T1003.001_%2520OS%2520Credent...024-09-13_dataset ;
            tb:has_position 0 ;
            tb:has_spec cb:implementation-data_partitioning-InputSpec-TabularDatasetShape ] ;
    tb:hasOutput [ a tb:Data ;
            tb:has_data ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning-output_1 ;
            tb:has_position 1 ;
            tb:has_spec cb:implementation-data_partitioning-OutputSpec-TestTabularDatasetShape ],
        [ a tb:Data ;
            tb:has_data ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning-output_0 ;
            tb:has_position 0 ;
            tb:has_spec cb:implementation-data_partitioning-OutputSpec-3973081919985400991 ] ;
    tb:has_position 1 ;
    tb:runs cb:component-top_k_absolute_train_test_split ;
    tb:usesParameter cb:implementation-data_partitioning-count_\(absolute_size\),
        cb:implementation-data_partitioning-fraction_\(relative_size\),
        cb:implementation-data_partitioning-sampling_method,
        cb:implementation-data_partitioning-size_type .

ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_2_implementation_numerical_projection a tb:Step ;
    tb:followedBy ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_3_implementation_xgboost_learner,
        ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_4_implementation_numeric_projection_predictor ;
    tb:hasInput [ a tb:Data ;
            tb:has_data ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_1_implementation_data_partitioning-output_0 ;
            tb:has_position 0 ;
            tb:has_spec cb:implementation-numerical_projection-InputSpec-TabularDatasetShape ] ;
    tb:hasOutput [ a tb:Data ;
            tb:has_data ab:workflow_0_I2Cat_070e6241_12d6_412c_87db_b72c526fc632-step_2_implementation_numerical_projection-output_0 ;
            tb:has_position 0 ;
            tb:has_spec cb:implementation-numerical_projection-OutputSpec-NumericOnlyTabularDatasetShape ] ;
    tb:has_position 2 ;
    tb:runs cb:component-projection_numerical_learner ;
    tb:usesParameter cb:implementation-numerical_projection-projected_columns,
        cb:implementation-numerical_projection-target_column .
  };
  ```
</div>

## Export to Python
<StepList
  steps={[
    { content: (
        <>
        Select a workflow and click the corresponding  <Button icon="download" iconSize="24px">PYTHON</Button> button. 
        <br/><br/>
        <Zoom>
        <img
            src={WePythonImg}
            alt="Translate to Python"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    }
  ]}
/>

The exported file will have this structure:
<div className="codeBlockWithTitle">
  <div className="codeBlockTitle">Xgboost Dart 0.py</div>
  ```python
  #This script has been automatically generated by I2WG
import pandas as pd

def DataLoading():
    return pd.read_parquet("datasets/jhGEmM91Bi0gVYetyN29r3N1qPsjDr8dkCQpQ2AS-Vs/T1003.001_%20OS%20Credent...024-09-13_dataset.parquet")


import sklearn.model_selection

def Partitioning(input0):
    output0, output1 = sklearn.model_selection.train_test_split(input0, random_state=None, shuffle=False, test_size=None, train_size=10)
    return  output0, output1


def DropColumns(data):
    columns = ['Access', 'Access_lag_1', 'Access_lag_11', 'Access_lag_16', 'Access_lag_21', 'Access_lag_26', 'Access_lag_31', 'Access_lag_36', 'Access_lag_41', 'malicious_label']
    return data[columns]


import xgboost

def XGBoost(X):
    Xt = X.drop(["malicious_label"],axis=1)
    yt = X["malicious_label"]
    model = xgboost.XGBClassifier(booster="dart", feature_selector="cyclic", grow_policy="depthwise", normalize_type="tree", objective="binary:logistic", sample_type="uniform")
    return model.fit(Xt, yt)

def DropColumns_predictor(data):
    columns = ['Access', 'Access_lag_1', 'Access_lag_11', 'Access_lag_16', 'Access_lag_21', 'Access_lag_26', 'Access_lag_31', 'Access_lag_36', 'Access_lag_41'']
    return data[columns]


import xgboost

def XGBoost_predictor(model,X):
    Xv = X.drop(["malicious_label"],axis=1)
    yp = model.predict(Xv)
    Xv["malicious_label"] = yp
    return Xv

import pandas

def DataStoring (result):
    pandas.DataFrame(result).to_csv(path_or_buf="./output.csv")

outputDataLoading0 = DataLoading() 
outputPartitioning0, outputPartitioning1 = Partitioning(outputDataLoading0) 
outputDropColumns0 = DropColumns(outputPartitioning0) 
outputXGBoost0 = XGBoost(outputDropColumns0) 
outputDropColumns_predictor0 = DropColumns_predictor(outputPartitioning0) 
outputXGBoost_predictor0 = XGBoost_predictor(outputXGBoost0, outputDropColumns_predictor0) 
DataStoring(outputXGBoost_predictor0) 
  ```
</div>

## Export to KNIME
<StepList
  steps={[
    { content: (
        <>
        Select a workflow and click the corresponding  <Button icon="download" iconSize="24px">KNIME</Button> button. 
        <br/><br/>
        Alternatively, If you want to export all the workflows to KNIME format, click <Button extra_class="select-button">DOWNLOAD ALL KNIME REPRESENTATIONS</Button> to get a <b>ZIP</b> file with all the translated workflows.
        <Zoom>
        <img
            src={WeKNIMEImg}
            alt="Translate to KNIME"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    }
  ]}
/>


## Export to XXP
<StepList
  steps={[
    { content: (
        <>
        Click <Button extra_class="dsl-button">DOWNLOAD INTENT TO DSL</Button> button. 
        <Zoom>
        <img
            src={WeXXPImg}
            alt="Translate to XXP"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    }
  ]}
/>

The exported file will have this structure:
<div className="codeBlockWithTitle" height="270px">
  <div className="codeBlockTitle">intent_to_xxp.zip</div>
    <Zoom>
        <img
            src={DSL}
            alt="DSL structure"
            style={{ width: 416, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
    </Zoom>
</div>
<br/>
<div className="codeBlockWithTitle">
  <div className="codeBlockTitle">I2CatWorkflow0.xxp</div>
  ``` python
  workflow I2CatWorkflow0 {

    START -> Partitioning -> DropColumns -> XGBoost -> DropColumns_test -> XGBoost_test -> END;

     
    task Partitioning; 
    task DropColumns; 
    task XGBoost; 
    task DropColumns_test; 
    task XGBoost_test;

    
    define input data T1003.001_%2520OS%2520Credent...024-09-13_dataset;
    configure data T1003.001_%2520OS%2520Credent...024-09-13_dataset {
        path "datasets/jhGEmM91Bi0gVYetyN29r3N1qPsjDr8dkCQpQ2AS-Vs/T1003.001_%20OS%20Credent...024-09-13_dataset.parquet";
    }
    

    
    define output data workflowOutput;
    configure data workflowOutput {
        path "/outputs/output.csv";
    }
    

    
    T1003.001_%2520OS%2520Credent...024-09-13_dataset --> Partitioning.PartitioningInput0;
    
    Partitioning.PartitioningOutput0 --> DropColumns.DropColumnsInput0;
    
    DropColumns.DropColumnsOutput0 --> XGBoost.XGBoostInput0;
    
    XGBoost_test.XGBoost_testOutput0 --> workflowOutput;
    
    Partitioning.PartitioningOutput0 --> DropColumns_test.DropColumns_testInput0;
    
    XGBoost.XGBoostOutput0 --> XGBoost_test.XGBoost_testInput0;
    
    DropColumns_test.DropColumns_testOutput0 --> XGBoost_test.XGBoost_testInput1;
    
    
}


workflow I2CatAssembledWorkflow0 from I2CatWorkflow0 {
    
    task Partitioning {
        implementation "top_k_absolute_train_test_split";
    }
    
    task DropColumns {
        implementation "projection_numerical_learner";
    }
    
    task XGBoost {
        implementation "xgboost_dart_learner";
    }
    
    task DropColumns_test {
        implementation "projection_numerical_predictor";
    }
    
    task XGBoost_test {
        implementation "xgboost_predictor";
    }
    

}

workflow I2CatAssembledWorkflow1 from I2CatWorkflow0 {
    
    task Partitioning {
        implementation "random_relative_train_test_split";
    }
    
    task DropColumns {
        implementation "projection_numerical_learner";
    }
    
    task XGBoost {
        implementation "xgboost_dart_learner";
    }
    
    task DropColumns_test {
        implementation "projection_numerical_predictor";
    }
    
    task XGBoost_test {
        implementation "xgboost_predictor";
    }
    

}

workflow I2CatAssembledWorkflow2 from I2CatWorkflow0 {
    
    task Partitioning {
        implementation "top_k_absolute_train_test_split";
    }
    
    task DropColumns {
        implementation "projection_numerical_learner";
    }
    
    task XGBoost {
        implementation "xgboost_tree_learner";
    }
    
    task DropColumns_test {
        implementation "projection_numerical_predictor";
    }
    
    task XGBoost_test {
        implementation "xgboost_predictor";
    }
    

}

workflow I2CatAssembledWorkflow3 from I2CatWorkflow0 {
    
    task Partitioning {
        implementation "random_relative_train_test_split";
    }
    
    task DropColumns {
        implementation "projection_numerical_learner";
    }
    
    task XGBoost {
        implementation "xgboost_tree_learner";
    }
    
    task DropColumns_test {
        implementation "projection_numerical_predictor";
    }
    
    task XGBoost_test {
        implementation "xgboost_predictor";
    }
    

}

workflow I2CatAssembledWorkflow4 from I2CatWorkflow0 {
    
    task Partitioning {
        implementation "top_k_relative_train_test_split";
    }
    
    task DropColumns {
        implementation "projection_numerical_learner";
    }
    
    task XGBoost {
        implementation "xgboost_tree_learner";
    }
    
    task DropColumns_test {
        implementation "projection_numerical_predictor";
    }
    
    task XGBoost_test {
        implementation "xgboost_predictor";
    }
    

}

workflow I2CatAssembledWorkflow5 from I2CatWorkflow0 {
    
    task Partitioning {
        implementation "random_absolute_train_test_split";
    }
    
    task DropColumns {
        implementation "projection_numerical_learner";
    }
    
    task XGBoost {
        implementation "xgboost_tree_learner";
    }
    
    task DropColumns_test {
        implementation "projection_numerical_predictor";
    }
    
    task XGBoost_test {
        implementation "xgboost_predictor";
    }
    

}
  ```
  </div>