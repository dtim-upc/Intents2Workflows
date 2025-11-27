<template>
    <div class="q-pa-md">
      <q-table :rows="intentsStore.abstractPlans" :columns="columns" :filter="search" row-key="id"  v-model:pagination="pagination"
               no-results-label="The filter didn't uncover any results">
  
        <!--<template v-slot:top-left="">
          <div class="q-table__title">
            Abstract plans
          </div>
        </template>
  
        <template v-slot:top-right="props">
  
          <q-input outlined dense debounce="400" color="primary" v-model="search">
            <template v-slot:append>
              <q-icon name="search"/>
            </template>
          </q-input>
  
          <FullScreenToggle :props="props" @toggle="props.toggleFullscreen"/>
        </template>-->

        <template v-slot:body-cell-visualize="props">
          <q-td :props="props">
            <q-btn color="primary" icon="mdi-eye-outline" @click="openDialog(props)"></q-btn>
            <DialogWithVisualizedPlan v-model:dialog="dialog" :visualizedPlan="visualizedPlan"/>
          </q-td>
        </template>

        <template v-slot:body-cell-select="props">
          <q-td :props="props">
            <q-checkbox v-model="intentsStore.selectedAlgorithms" :val="props.row.name"/>
          </q-td>
        </template>

        <template v-slot:no-data>
          <div class="full-width row flex-center text-accent q-gutter-sm q-pa-xl" style="flex-direction: column">
            <NoDataImage/>
            <span style="color: rgb(102, 102, 135);font-weight: 500;font-size: 1rem;line-height: 1.25;">No data products.</span>
          </div>
        </template>
  
      </q-table>
    </div>
  </template>
  
  <script setup>
  import { ref} from "vue";
  import {useIntentsStore} from 'src/stores/intentsStore.js'
  import NoDataImage from "src/assets/NoDataImage.vue";
  import FullScreenToggle from "./TableUtils/FullScreenToggle.vue";
  import DialogWithVisualizedPlan from "../../components/intents/visualize_plan/DialogWithVisualizedPlan.vue";

  
  const intentsStore = useIntentsStore()
  const selectedPlans = ref(intentsStore.abstractPlans); 


  intentsStore.selectedAlgorithms = []
  selectedPlans.value.map(absPlan => {
    intentsStore.selectedAlgorithms.push(absPlan.name)
  })

  console.log(intentsStore.selectedAlgorithms)
  
  const dialog = ref(false)
  const visualizedPlan = ref(null)
  
  const search = ref("")

  const columns = [
    {name: "select", label:"", align:"center", field: "select", sortable: false},
    {name: "fileName", label: "Algorithm", align: "center", field: "name", sortable: true},
    {name: "loss", label:"Loss", align:"center", field: "loss", sortable: true},
    {name: "accuracy", label:"Accuracy", align:"center", field: "accuracy", sortable: true},
    {name: "recall", label:"Recall", align:"center", field: "recall", sortable: true},
    {name: "f1_score", label:"F1", align:"center", field: "f1_score", sortable: true},
    {name: "training_time", label: "Training Time", align:"center", field: "training_time", sortable: true},
    {name: "score", label:"Utility", align:"center", field: "score", sortable: true},
    {name: "visualize", label:"", align:"center", field: "visualize", sortable: false},
  ]


  const pagination = ref({
  page: 1,
  rowsPerPage: 15,
  sortBy: 'score',     
  descending: true, 
  })


  const openDialog = (propsRow) => {
  visualizedPlan.value = propsRow.row.plan
  dialog.value = true
  }


  const isSelected = (row) => {
    return row.selected
  }

  const toggleRow = (row) => {
    row.selected = !row.selected;
  }

  </script>
  