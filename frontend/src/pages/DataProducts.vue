<template>
  <q-page>
    <TableDataProducts/>

    <!-- File Upload Button -->
    <q-btn label="Upload CSV" @click="triggerFileInput" color="primary" style="margin-left: 20px;"/>

    <!-- File Input (Hidden, triggered by button) -->
    <input ref="fileInput" type="file" accept=".csv" style="display: none;" @change="handleFileUpload" />

  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import TableDataProducts from 'components/tables/TableDataProducts.vue';
import { useDataProductsStore } from 'src/stores/dataProductsStore';
import {odinApi} from 'boot/axios';
import { useNotify } from 'src/use/useNotify.js';

const dataProductsStore = useDataProductsStore()
const notify = useNotify();

// References
const fileInput = ref(null);

// Trigger file input click when button is clicked
const triggerFileInput = () => {
  fileInput.value.click();
};

// Handle file selection and read the file
const handleFileUpload = (event) => {
  const file = event.target.files[0];

  //Special case when using firefox and windows, where a csv file is interpreted as excel file type
  const csvFirefoxWindowsImport = file && file.type === 'application/vnd.ms-excel' && file.name.split('.').pop() === 'csv'

  if (file && (file.type === 'text/csv' || csvFirefoxWindowsImport) ) {

    sendFileToBackend(file);
  }
};

// Function to send the CSV file to the backend
const sendFileToBackend = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await odinApi.post('/data-product', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    if (response.status === 200) {
      notify.positive("Data product stored successfully");
    } else {
      throw new Error('Upload failed');
    }
  } catch (error) {
    notify.negative("Error storing the data product");
  }
  dataProductsStore.getDataProducts()
};
</script>
