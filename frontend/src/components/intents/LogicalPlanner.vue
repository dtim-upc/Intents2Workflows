<template>
  <q-page>
    <q-form class="row q-col-gutter-md text-center justify-center" @submit.prevent="handleSubmit">            
      <div class="col-12">
        <h4> Logical planner </h4>
        <h6> Select the Abstract Plans to send to the Logical Planner: </h6>
      </div>
      <div v-if="intentsStore.abstractPlans.length === 0">
        <h6 style="color: red;">No query selected</h6>
      </div>
      <div v-else class="col-6 text-left">
        <q-list bordered separator>
          <q-item v-for="(absPlan) in intentsStore.abstractPlans"
                  :key="absPlan.id" class="q-my-sm">
            <q-item-section avatar>
              <q-checkbox v-model="selectedPlans" :val="absPlan"/>
            </q-item-section>
            <q-item-section> 
              <text-body1 style="font-size: 17px;"> {{ absPlan.name }}</text-body1>
            </q-item-section>
            <q-item-section side> 
              <text-body1 style="font-size: 17px;"> {{ absPlan.score }}</text-body1>
            </q-item-section>
            <q-item-section avatar>
              <q-btn color="primary" icon="mdi-eye-outline" @click="openDialog(absPlan.plan)">
              </q-btn>
            </q-item-section>
          </q-item>
        </q-list>

        <DialogWithVisualizedPlan v-model:dialog="dialog" :visualizedPlan="visualizedPlan"/>
      </div>
      <div class="col-12">
        <q-btn label="Run logical planner" color="primary" type="submit" :disabled="get_num_selected_plans() == 0"/>
      </div>
      <div class="col-12">
        <q-btn label="Select all" @click="selectAll()"/>
        <q-btn label="Select none" @click="selectNone()" class="q-ml-sm"/>
      </div>
    </q-form>
  </q-page>
</template>

<script setup>
import {ref} from 'vue'
import {useIntentsStore} from 'stores/intentsStore.js'
import {useDataProductsStore} from 'stores/dataProductsStore';
import DialogWithVisualizedPlan from "../../components/intents/visualize_plan/DialogWithVisualizedPlan.vue";
import {useRoute, useRouter} from "vue-router";
import { useQuasar } from 'quasar'

const router = useRouter()
const route = useRoute()
const intentsStore = useIntentsStore()
const dataProductsStore = useDataProductsStore()
const $q = useQuasar()

const dialog = ref(false)
const visualizedPlan = ref(null)

console.log(intentsStore.abstractPlans)

const selectedPlans = ref(intentsStore.abstractPlans); 

const get_num_selected_plans = () => {
  return selectedPlans.value.length
}
        
const handleSubmit = async() => {
  $q.loading.show({message: 'Running logical planner'})
  const successCallback = () => {
    router.push({ path: route.path.substring(0, route.path.lastIndexOf("/")) + "/workflow-planner" })
  }

  //await dataProductsStore.getDataProductAnnotations(intentsStore.selectedDataProdutName)

  intentsStore.selectedAlgorithms = []
  selectedPlans.value.map(absPlan => {
    intentsStore.selectedAlgorithms.push(absPlan.name)
  })

  intentsStore.getShapeGraph()
  const data = {"shape_graph": intentsStore.getShapeGraph(), "intent_graph":intentsStore.intent_graph, 'dataset':dataProductsStore.selectedDataProductAnnotations}

  await intentsStore.setLogicalPlans(data, successCallback)
  $q.loading.hide()
}

const selectAll = () => {
  intentsStore.abstractPlans.forEach(absPlan => {
    absPlan.selected = true
  });
  selectedPlans.value = intentsStore.abstractPlans
}

const selectNone = () => {
  intentsStore.abstractPlans.forEach(absPlan => {
    absPlan.selected = false
  });
  selectedPlans.value = []
}

const openDialog = (plan) => {
  visualizedPlan.value = plan
  dialog.value = true
}

</script>