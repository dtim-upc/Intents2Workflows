<template>
    <DDMLogin v-model="isLoginVisible"/>
    <q-page padding>
        <div class="row q-col-gutter-md text-center justify-center">            
            <div class="col-12">
              <h4> Final workflows </h4>
            </div>
            <div v-if="intentsStore.selectedPlans.length === 0">
              <h6 style="color: red;">No workflows selected</h6>
            </div>
              <div v-else class="col-12 col-lg-8 text-left">
                <q-list bordered separator>
                  <q-item v-for="(group, index) in intentsStore.selectedPlans" :key="index" class="q-my-sm">
                    <q-item-section> 
                      <text-body1 style="font-size: 17px;"> {{ group.id }} </text-body1>
                    </q-item-section>
                    <div >
                      <q-expansion-item label="Individual plans" style="font-size: 17px; background-color: rgb(243, 241, 241);">
                        <q-list bordered separator>
                          <q-item v-for="(plan, indexPlan) in group.plans" :key="indexPlan" class="q-my-sm">
                          <q-item-section> {{ plan.id }}</q-item-section>
                          <q-item-section avatar>
                            <q-btn color="primary" icon="mdi-eye-outline" size="10px" @click="openDialog(plan.plan)" style="font-size: 14px;"/>
                          </q-item-section>
                          <q-item-section avatar>
                            <q-btn color="primary" icon="mdi-database" size="10px" @click="storeWorkflowDialog(plan)" label="Store" style="font-size: 14px;"/>
                          </q-item-section>
                          <q-item-section avatar>
                            <q-btn color="primary" icon="mdi-download" size="10px" @click="intentsStore.downloadRDF(plan)" label="RDF" style="font-size: 14px;"/>
                          </q-item-section>
                          <q-item-section avatar>
                            <q-btn color="primary" icon="mdi-download" size="10px" @click="intentsStore.downloadKNIME(plan)" label="KNIME" style="font-size: 14px;" :disabled="!plan.KNIMECompatible"/>
                          </q-item-section>
                          <q-item-section avatar>
                            <q-btn color="primary" icon="mdi-download" size="10px" @click="intentsStore.downloadPython(plan)" label="Python" style="font-size: 14px;" :disabled="!plan.PythonCompatible"/>
                          </q-item-section>
                          <q-item-section avatar>
                            <q-btn color="primary" icon="mdi-download" size="10px" @click="intentsStore.downloadProactive(plan)" label="Proactive" style="font-size: 14px;" />
                          </q-item-section>
                          </q-item>
                        </q-list>
                      </q-expansion-item>
                    </div>
                  </q-item>
                </q-list>
                
            </div>
            <div class="col-12">
              <q-btn label="Download all RDF representations" @click="intentsStore.downloadAllRDF()"/>
              <q-btn label="Download all KNIME representations" @click="intentsStore.downloadAllKNIME()" class="q-ml-sm"/>
              <q-btn label="Download Intent to DSL" color="purple" class="q-ml-sm"@click="intentsStore.downloadAllDSL()"/>
              <q-btn label="Export to XXP FSS" color="purple" class="q-ml-sm"@click="exportToFS()"/>
            </div>
        </div>
    </q-page>

    <DialogWithVisualizedPlan v-model:dialog="dialog" :visualizedPlan="visualizedPlan"/>

    <q-dialog v-model="storeWorkflowDialogBoolean">
      <q-card>
        <q-card-section>
          <q-form @submit="storeWorkflow" class="text-right">
            <q-input v-model="workflowName" label="Workflow name" :rules="[ val => val && val.length > 0 || 'Insert a name']"/>
            
            <q-btn type="submit" color="primary" label="Store" v-close-popup/>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import {useIntentsStore} from 'stores/intentsStore.js'
import {useWorkflowsStore} from 'stores/workflowsStore.js'
import { useNotify } from 'src/use/useNotify.js';
import DialogWithVisualizedPlan from "../../components/intents/visualize_plan/DialogWithVisualizedPlan.vue";
import { useQuasar } from 'quasar'
import {intentsApi} from 'boot/axios';
import FileSaver from 'file-saver';
import { useDdmStore } from 'src/stores/ddmStore';
import DDMLogin from "src/components/utils/DDMLogin.vue";

const ddmStore = useDdmStore();
const intentsStore = useIntentsStore()
const workflowsStore = useWorkflowsStore()
const $q = useQuasar()
const notify = useNotify();


const storeWorkflowDialogBoolean = ref(false)
const dialog = ref(false)

const selectedPlan = ref(null)
const workflowName = ref("")
const visualizedPlan = ref(null)
const isLoginVisible = ref(false);

var ddmbearerToken = "";

// Watch for login status changes and react accordingly
watch(() => ddmStore.token, async (newToken) => {
  if (newToken) {
    ddmbearerToken = newToken;
  }
});

const openDialog = (plan) => {
  visualizedPlan.value = plan
  dialog.value = true
}

const storeWorkflowDialog = (plan) => {
  console.log(intentsStore.selectedPlans)
  selectedPlan.value = plan
  storeWorkflowDialogBoolean.value = true
}

const storeWorkflow = async () => {
  const data = {
    workflowName: workflowName.value,
    visualRepresentation: selectedPlan.value.plan,
    stringGraph: selectedPlan.value.graph
  };
  const intentID = intentsStore.intentID

  workflowsStore.postWorkflow(intentID, data)
}

const exportToFS = async () => {
  // Trigger login modal visibility when this button is clicked

  if (ddmStore.token) {
    isLoginVisible.value = false
    $q.loading.show({message: 'Exporting workflows'})
    await intentsStore.exportToXXP(ddmStore.user)
    $q.loading.hide()
  }
  else {
      isLoginVisible.value = true;
  }

}


</script>
