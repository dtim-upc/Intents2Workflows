<template>
    <q-page>
        <q-form class="row text-center justify-center" @submit.prevent="handleSubmit" @reset="resetForm">            
            <div class="col-12">
                <h4> Abstract Planner </h4>
            </div>
            <div class="col-12" style="padding-left: 12px;">
                <div class="text-body1 text-left"> General intent information </div>
            </div>
            <div class="col-4" style="padding: 10px;">
              <q-input label="Intent name" outlined v-model="intentName" class="q-mb-sm" disable
                    :rules="[ val => val && val.length > 0 || 'Insert a name']"/>
            </div>
            <div class="col-4" style="padding: 10px;">
              <q-select label="Data product" outlined v-model="selectedDataProdutName" disable class="q-mb-sm"
                :rules="[ val => val && val.length > 0 || 'Select a dataset']"/>
            </div>
            <div class="col-4" style="padding: 10px;">
              <q-select label="Problem" outlined v-model="problem" disable class="q-mb-sm"
                    :rules="[ val => val && val.length > 0 || 'Select a problem']"/>
            </div>
            <div class="col-12" style="padding-left: 12px;">
                <div class="text-body1 text-left"> Problem-specific information </div>
            </div>
            <div class="col-4" style="padding: 10px;">
              <q-select v-if="selectedDataProdutName && problem ==='Classification'" label="Target variable" outlined v-model="target" disable class="q-mb-sm"
                    :rules="[ val => val && val.length > 0 || 'Select a target variable']"/>
            </div>
            <div class="col-4"></div>
            <div class="col-4"></div>
            <div class="col-12" style="padding-left: 12px;">
                <div class="text-body1 text-left"> Configuration </div>
            </div>

            <div class="col-3" style="padding: 10px; display: flex; align-items: center;">
              <q-select
                label="Restrict Algorithm"
                outlined
                v-model="selectedAlgorithm"
                :options="algorithmOptions"
                option-label="label"
                class="q-mb-sm"
                style="flex: 1;"
                :rules="[ val => val && val.label && val.label.length > 0 || 'Select an algorithm']"
              >
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section>
                      <q-item-label>
                        {{ scope.opt.label }}
                        <span v-if="scope.opt.recommendation">💡</span>
                      </q-item-label>
                      <div
                        v-if="scope.opt.recommendation"
                        style="white-space: normal; line-height: 1.3; font-size: 12px; color: rgba(0, 0, 0, 0.6); margin-top: 2px;"
                      >
                        {{ scope.opt.recommendation }}
                      </div>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>

          

            <div class="col-12">
                <q-btn label="Run Abstract Planner" color="primary" type="submit"/>
                <q-btn label="Reset" type="reset" class="q-ml-sm"/>
                
            </div>
        </q-form>
    </q-page>
</template>

<script setup>
import {ref, onMounted, computed} from 'vue'
import {useIntentsStore} from 'stores/intentsStore.js'
import {useDataProductsStore} from 'stores/dataProductsStore.js'
import {useRoute, useRouter} from "vue-router";
import {useQuasar} from 'quasar'

const router = useRouter()
const route = useRoute()
const $q = useQuasar()

const intentsStore = useIntentsStore()
const dataProductsStore = useDataProductsStore()

const intentName = computed({ get: () => intentsStore.intentName})
const selectedDataProdutName = computed({ get: () => intentsStore.selectedDataProdutName})
const problem = computed({ get: () => intentsStore.selectedProblem})
const target = computed({ get: () => intentsStore.target})


const selectedAlgorithm = computed({
  get: () => {
    // Set default to 'No Restriction' (value: null)
    const selected = intentsStore.selectedAlgorithm;
    return algorithmOptions.value.find(opt => opt.value === selected) || algorithmOptions.value[0]; // default to 'No Restriction'
  },
  set: (obj) => {
    // Set value of selected algorithm
    intentsStore.selectedAlgorithm = obj?.value || null; // Set 'No Restriction' if null
  }
});



const algorithmOptions = computed(() => {
  return [
    { label: 'No Restriction', value: null, recommendation: '' }, // Default option
    ...intentsStore.algorithmRecommendations.map(([alg, explanation]) => ({
      label: alg,
      value: alg,
      recommendation: explanation
    }))
  ];
});


const getRecommendation = (algName) => {
  const match = algorithmOptions.value.find(opt => opt.value === algName);
  return match?.recommendation || '';
};

const handleSubmit = async() => {
  const selectedDataProduct = dataProductsStore.dataProducts.find(dp => dp.name === selectedDataProdutName.value);

  $q.loading.show({message: 'Creating intent...'}) // First, create the intent object in the backend
  let data = new FormData();
  data.append("intent_name", intentName.value);
  data.append("problem", intentsStore.problems[problem.value]);
  data.append("data_product", selectedDataProduct.name)

  await intentsStore.postIntent(data)
  await intentsStore.getAllIntents() // Refresh the list of intents

  //$q.loading.show({message: 'Materializing data product...'}) // Then, create the csv file from the dataProduct
  //await dataProductsStore.materializeDataProduct(projectID, selectedDataProduct.id)

  /*$q.loading.show({message: 'Annotating query...'}) // Then, annotate the dataset and define the new ontology
  data = {
    'path': selectedDataProduct.path,
    'label': target.value,
  }
  await intentsStore.annotateDataset(data)*/

  $q.loading.show({message: 'Getting annotations...'})
  let label_data = new FormData();
  label_data.append('label', intentsStore.target)

  await dataProductsStore.getDataProductAnnotations(selectedDataProduct.name,label_data)
  //await dataProductsStore.getDataProductAnnotations(selectedDataProduct.name)

  $q.loading.show({message: 'Running abstract planner...'}) // Finally, run the planner
  data = {
    'intent_name': intentName.value,
    'dataset': dataProductsStore.selectedDataProductURI,
    'problem': intentsStore.problems[problem.value],
    'experiment_constraints': [
        {'GPU': true},
        {'testing': [8, 10]}
    ],
  }

  const successCallback = () => {
    router.push({ path: route.path.substring(0, route.path.lastIndexOf("/")) + "/logical-planner" })
  }

  await intentsStore.setAbstractPlans(data, successCallback)
  $q.loading.hide() 
}

const resetForm = () => {
  intentName.value = null
  query.value = null
  problem.value = null
}

onMounted(async() => {
  await dataProductsStore.getDataProducts()
  intentsStore.getProblems()
})

</script>
