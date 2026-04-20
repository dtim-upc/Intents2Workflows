<template>
  <div>
    <q-dialog v-model="dialogVisible" persistent :maximized="maximizedToggle" transition-show="slide-up" transition-hide="slide-down">
      <q-card class="text-black">
        <q-bar>
          <q-space />
          <q-btn 
            dense 
            flat 
            icon="minimize" 
            @click="maximizedToggle = false" 
            :disable="!maximizedToggle"
            tooltip="Minimize"
            tooltip-class="bg-white text-primary"
          />
          <q-btn 
            dense 
            flat 
            icon="crop_square" 
            @click="maximizedToggle = true" 
            :disable="maximizedToggle"
            tooltip="Maximize"
            tooltip-class="bg-white text-primary"
          />
          <q-btn 
            dense 
            flat 
            icon="close" 
            @click="close"
            tooltip="Close"
            tooltip-class="bg-white text-primary"
          />
        </q-bar>

        <q-card-section style="height: calc(100vh - 100px); overflow: auto;">
          <VisualizePlan 
            v-if="dialogVisible"
            :plan="visualizedPlan" 
            :cols="visualizedPlanCols"
          /> 
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>

import { computed, ref } from 'vue';
import VisualizePlan from './VisualizePlan.vue';

const props = defineProps({
  dialog: { type: Boolean, required: true },
  visualizedPlan: { type: Object, required: true },
  visualizedPlanCols: { type: Object, required: false, default: () => ({}) }
});

const emit = defineEmits(['update:dialog']);

const dialogVisible = computed({
  get: () => props.dialog,
  set: (val) => emit('update:dialog', val)
});

const maximizedToggle = ref(true);

const close = () => {
  dialogVisible.value = false;
};
</script>
