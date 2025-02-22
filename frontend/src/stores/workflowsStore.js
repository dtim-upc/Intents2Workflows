import { defineStore } from 'pinia';
import { useNotify } from 'src/use/useNotify.js';
import workflowAPI from "src/api/workflowAPI.js";
import download from 'downloadjs'
import { useIntentsStore } from "src/stores/intentsStore.js";

const notify = useNotify();

export const useWorkflowsStore = defineStore('store', {
  state: () => ({}),

  actions: {

    // ---------------- CRUD Operations
    async postWorkflow(intentID, data) {
      try {
        await workflowAPI.postWorkflow(intentID, data);
        notify.positive(`Workflow stored`);
      } catch (error) {
        notify.negative("Error storing the workflow");
        console.error("Error:", error);
      }
    },

    /* async putWorkflow(intentID, projectID, workflowID, data, successCallback) {
      try {
        await workflowAPI.putWorkflow(intentID, projectID, workflowID, data);
        notify.positive(`Workflow successfully edited`);
        useIntentsStore().getAllIntents(projectID); // Refresh the intents and, as such, the workflows
        successCallback();
      } catch (error) {
        notify.negative("Error editing the workflow");
        console.error("Error:", error);
      }
    }, */

    async deleteWorkflow(intentName, workflowName) {
      try {
        await workflowAPI.deleteWorkflow(intentName, workflowName);
        notify.positive(`Workflow deleted successfully`);
        useIntentsStore().getAllIntents(); // Refresh the intents and, as such, the workflows
      } catch (error) {
        notify.negative("Error deleting the workflow.");
        console.error("Error:", error);
      }
    },

    // ---------------- Graph related operations

    async downloadWorkflowSchema(workflow) {
      try {
        //const response = await workflowAPI.downloadWorkflowSchema(projectID, intentID, workflow.workflowID)
        //const content = response.headers['content-type']
        /*response.data.text().then(textContent => {
          console.log(textContent)
        })*/

        download(workflow.graph, workflow.name + ".ttl")
      } catch (error) {
        console.error("Error:", error)
        notify.negative("Error downloading the schema")
      }
    },
  }
});