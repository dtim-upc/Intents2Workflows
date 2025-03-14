import {intentsApi} from 'boot/axios';
import {odinApi} from 'boot/axios';
import {textToIntentAPI} from 'boot/axios';
import {intentToGraphDBAPI} from 'boot/axios';

export default {

  // Intent2Workflow calls

  postIntent(data) {
    return odinApi.post('/intent', data)
  },
  getAllIntents() {
    return odinApi.get('/intents')
  },
  deleteIntent(intentName) {
    return odinApi.delete('/intent/' + intentName)
  },
  putIntent(intentID, projectID, data) {
    return odinApi.put('/project/' + projectID + '/intent/' + intentID, data)
  },
  annotateDataset(data) {
    return intentsApi.post('/annotate_dataset', data)
  },
  getProblems() {
    return intentsApi.get('/problems')
  },
  setAbstractPlans(data) {
    return intentsApi.post('/abstract_planner', data)
  },
  setLogicalPlans(data) {
    return intentsApi.post('/logical_planner', data)
  },
  downloadKNIME(data) {
    return intentsApi.post('/workflow_plans/knime', data, {responseType: 'blob'})
  },
  downloadAllKNIME(data) {
    return intentsApi.post(`/workflow_plans/knime/all`, data, {responseType: 'blob'})
  },
  downloadAllDSL(data) {
    return intentsApi.post('/intent-to-dsl', data, {responseType: 'blob'})
  },
  downloadProactive(data) {
    return intentsApi.post('/workflow_plans/proactive', data, {responseType: 'blob'})
  },

  // Intent anticipation calls
  predictIntentType(data) {
    return textToIntentAPI.post('/predictIntent', data)
  },
  addUser(data) {
    return intentToGraphDBAPI.post('/add_user', data)
  },
  addDataset(data) { // Add dataset to graphDB
    return intentToGraphDBAPI.post('/add_dataset', data)
  },
  getRecommendation(email, dataset, problem) {
    return intentToGraphDBAPI.get('/get_recommendations?user=' + email + "&dataset=" + dataset + "&intent=" + problem)
  },
  getAllInfo() {
    return intentToGraphDBAPI.get('/get_all_info')
  },
}