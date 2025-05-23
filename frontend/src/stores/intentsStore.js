import {defineStore} from 'pinia'
import {useNotify} from 'src/use/useNotify.js'
import intentsAPI from "src/api/intentsAPI.js";
import JSZip from 'jszip';
import FileSaver from 'file-saver';

const notify = useNotify();

export const useIntentsStore = defineStore('intents', {

  state: () => ({
    intents: [], // List of intents in the system (ODIN objects)
    problems: [], // List of problems available for the user to select when creating an intent
    intentID: "", // ID of the current intent (ODIN object), used to associate the workflows that are stored to it
    
    selectedProblem: "", // Problem selected by the user, either manually or via inference
    intentName: "", 
    selectedDataProdutName:"",
    intentDescription:"", // To infer the problem based on a description

    target:"", // Only for classification tasks

    selectedMetric: "",
    allMetrics: [],
    selectedPreprocessing: "",
    selectedPreprocessingAlgorithm: "",
    allPreprocessingAlgorithms: [],
    algorithmRecommendations: [],
    selectedAlgorithms: [],
    allAlgorithms: [],

    dataProductURI: "", // URI of the selected data product. This is required given that when working with graphs we need URIs
    intent_graph: {}, // Graph definition of the current intent
    algorithmImplementations: [], // List of algorithms defined in the ontology
    labelColumn: "", // Column over which a classification model will operate. ONLY FOR INTEGRATION WITH PROACTIVE. SHOULD BE REMOVED WHEN INTEGRATION DEPENDS ON THE GRAPH
    
    abstractPlans: [], // List of abstract plans (displayed in Logical Planner)
    logicalPlans: [], // List of logical plans (displayed in Workflow Planner)
    selectedPlans: [], // List of selected plans by the user (Displayed in Workflows)
    countSelectedPlans: 0 // Number of selected plans by the user
  }),

  actions: {

    // ------------ CRUD operations
    async getAllIntents() {
      try {
        const response = await intentsAPI.getAllIntents();
        this.intents = response.data.intents || [];
      } catch (error) {
        console.error("Error retrieving intents:", error);
        console.error("Error:", error);
      }
    },

    async postIntent(data) {
      try {
        const response = await intentsAPI.postIntent(data);
        notify.positive("Intent created");
        this.intentID = response.data.intent_name;
      } catch (error) {
        notify.negative("Error creating an intent.");
        console.error("Error:", error);
      }
    },
    
/*     async putIntent(intentID, projectID, data, successCallback) {
      try {
        await intentsAPI.putIntent(intentID, projectID, data);
        notify.positive(`Intent successfully edited`);
        this.getAllIntents(projectID);
        successCallback();
      } catch (error) {
        notify.negative("Error editing an intent.");
        console.error("Error:", error);
      }
    }, */

    async deleteIntent(intentName) {
      try {
        const response = await intentsAPI.deleteIntent(intentName);
        notify.positive(`Intent deleted successfully`);
        this.getAllIntents();
      } catch (error) {
        notify.negative("Error deleting an intent.");
        console.error("Error:", error);
      }
    },
    
    // ------------ Plan generation operations
    async getProblems() {
      try {
        const response = await intentsAPI.getProblems();
        this.problems = response.data || [];
      } catch (error) {
        console.error("Error:", error);
      }
    },
    
    async setAbstractPlans(data, successCallback) {
      try {
        const response = await intentsAPI.setAbstractPlans(data);
        notify.positive(`Abstract plans created`)
        this.intent_graph = response.data.intent
        this.algorithmImplementations = response.data.algorithm_implementations
        this.abstractPlans = Object.entries(response.data.abstract_plans).map(([plan, value]) => ({
          name: plan.split('#').at(-1),
          id: plan,
          selected: true,
          plan: value
        }));
        this.logicalPlans = [];
        this.selectedPlans = [];
        successCallback();
      } catch (error) {
        notify.negative("Error creating the abstract plans.");
        console.error("Error:", error);
      }
    },
    
    async setLogicalPlans(data, successCallback) {
      try {
        const response = await intentsAPI.setLogicalPlans(data);
        notify.positive(`Logical plans created`);
        // Formatting the plans to be displayed in the UI
        const keys = Object.keys(response.data);
        this.logicalPlans = [];
        this.countSelectedPlans = 0;
      
        for (let key of keys) {
          let found = false
          const plan = {
            id: key,
            selected: true,
            plan: response.data[key].logical_plan,
            graph:  response.data[key].graph,
            knimeCompatible: response.data[key].knimeCompatible
          }
          this.logicalPlans.map(logPlan => {
            if (logPlan.id === this.removeLastPart(key)) {
              logPlan.plans.push(plan)
              found = true
            }
          })
          if (!found) {
            this.logicalPlans.push({
              id: this.removeLastPart(key),
              selected: true,
              plans: [plan]
            })
          }
          this.countSelectedPlans++
        }
        this.selectedPlans = []
        successCallback();
      } catch (error) {
        notify.negative("Error creating the logical plans.");
        console.error("Error:", error);
      }
    },
    
    removeLastPart(inputString) {
      const parts = inputString.split(' ');
      if (parts.length > 1) {
        parts.pop(); // Remove the last part
        return parts.join(' ');
      } else {
        return inputString; // Return the original string if there's only one part
      }
    },

    // ------------ Download operations
    async downloadRDF(plan) {
      try {
        FileSaver.saveAs(new Blob([plan.graph]), `${plan.id}.ttl`);
        notify.positive(`RDF file downloaded`);
      } catch (error) {
        notify.negative("Error downloading the RDF file");
        console.error("Error:", error);
      }
    },
    
    async downloadKNIME(plan) {
      const data = {"graph": plan.graph, "plan_id": plan.id}
      try {
        const response = await intentsAPI.downloadKNIME(data);
        FileSaver.saveAs(new Blob([response.data]), `${plan.id}.knwf`);
        notify.positive(`KNIME file downloaded`);
      } catch (error) {
        notify.negative("Error downloading the KNIME file");
        console.error("Error:", error);
      }
    },

    async downloadProactive(plan) {
      console.log(this.intents)
      console.log(this.intentName)
      //const currentIntent = this.intents.find(intent => intent.name === String(this.intentName)) // SHOULD BE REMOVED EVENTUALLY
      const dataProductName = this.selectedDataProdutName//currentIntent.dataProduct.datasetName // SHOULD BE REMOVED EVENTUALLY
      // At some point, the translation to the Proactive ontology should be done, and the API should only require the graph to make it
      const data = {"graph": plan.graph, "layout": plan.plan, "label_column": this.labelColumn, "data_product_name": dataProductName}
      try {
        const response = await intentsAPI.downloadProactive(data);
        FileSaver.saveAs(new Blob([response.data]), `${plan.id}.xml`);
        notify.positive(`Proactive file downloaded`);
      } catch (error) {
        notify.negative("Error downloading the KNIME file");
        console.error("Error:", error);
      }
    },

    getSelectedGraphs() {
      const graphs = {}
      for (const [key, value] of Object.entries(this.selectedPlans)) {
        for (const plan of value.plans) {
          const { graph, id } = plan
          graphs[id] = graph
        }
      }
      return graphs
    },
    
    async downloadAllRDF() {
      const zip = new JSZip();
      try {
        for (const [key, value] of Object.entries(this.getSelectedGraphs())) {
          zip.file(key + ".ttl", value);
        }
        zip.generateAsync({ type: 'blob' }).then(function (content) {
          FileSaver.saveAs(content, 'rdf-files.zip');
        });
        notify.positive(`All RDF files downloaded`);
      } catch (error) {
        notify.negative("Error downloading all the RDF files");
        console.error("Error:", error);
      }
    },
    
    async downloadAllKNIME() {
      const data = {"graphs": this.getSelectedGraphs()}
      try {
        const response = await intentsAPI.downloadAllKNIME(data);
        FileSaver.saveAs(new Blob([response.data]), `knime.zip`);
        notify.positive(`All RDF files downloaded`);
      } catch (error) {
        notify.negative("Error downloading all the KNIME files");
        console.error("Error:", error);
      }
    },

    async downloadAllDSL() {
      const data = {"graphs": this.getSelectedGraphs()}
      try {
        const response = await intentsAPI.downloadAllDSL(data);
        FileSaver.saveAs(new Blob([response.data]), `intent_to_dsl.xxp`);
        notify.positive(`XXP file downloaded`);
      } catch (error) {
        notify.negative("Error downloading the XXP files");
        console.error("Error:", error);
      }
    },

    // ------------ Intent anticipation
  
    async predictIntentType(data) {
      try {
        const response = await intentsAPI.predictIntentType(data);
        notify.positive(`Type of intent predicted`);
        this.selectedProblem = response.data.intent
      } catch (error) {
        notify.negative("Error predicting an intent.");
        console.error("Error:", error);
      }
    },

    async predictParameters() {
      const user = "testuser"
      const dataset = this.selectedDataProdutName 
      const intent = this.selectedProblem 

      let response = await intentsAPI.getRecommendation(user, dataset, intent);
      this.algorithmRecommendations = response.data.algorithm; //TODO display these recommendations with explanation

      this.selectedAlgorithms = []
    },

    async getAllInfo() {
      const response = await intentsAPI.getAllInfo();
      this.allMetrics = response.data.metrics
      this.allAlgorithms = response.data.algorithms
      this.allPreprocessingAlgorithms= response.data.preprocessing_algorithms

      this.allAlgorithms = ["DecisionTree", "XGBoost", "SVM"]
    },

    getShapeGraph() {

        // Generate one `sh:hasValue` line per element
      const hasValueLines = this.selectedAlgorithms
        .map(alg => `[sh:hasValue "${alg}"]`)
        .join("\n");

      const shape_graph = 
        `@prefix ab: <https://extremexp.eu/ontology/abox#> .
        @prefix cb: <https://extremexp.eu/ontology/cbox#> .
        @prefix dmop: <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#> .
        @prefix tb: <https://extremexp.eu/ontology/tbox#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        
        ab:AlgorithmConstraint
          a sh:NodeShape ;
          #sh:targetClass tb:Algorithm ; #Not needed (ignored by validate function), but it clarifies the purpose of the constraint
          sh:property [
            sh:path rdfs:label ;
            sh:or (
            ${hasValueLines}
            );
            
          ].`

      return (this.selectedAlgorithms.length > 0 && this.selectedAlgorithms.some(item => item != null)) ? shape_graph : ""
    }
  }
})
