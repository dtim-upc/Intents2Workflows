<template>
  <q-page>
    <TableDataProducts/>

    <!-- File Upload Button -->
    <q-btn label="Upload File" @click="triggerFileInput" color="primary" style="margin-left: 20px;"/>

    <!-- Folder Upload Button -->
    <q-btn label="Upload Folder" @click="triggerFolderInput" color="primary" style="margin-left: 20px;"/>

    <q-btn label="Upload DDM" @click="triggerDDM" color="primary" style="margin-left: 20px;"/>

    <!-- File Input (Hidden, triggered by button) -->
    <input ref="fileInput" type="file" accept=".csv, .parquet, .zip, .npz, .las" style="display: none;" @change="handleFileUpload" multiple/>
    <input ref="folderInput" type="file" accept="*" style="display: none;" @change="handleFileUpload"  webkitdirectory = "true" directory/>


  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import TableDataProducts from 'components/tables/TableDataProducts.vue';
import { useDataProductsStore } from 'src/stores/dataProductsStore';
import {odinApi} from 'boot/axios';
import { useNotify } from 'src/use/useNotify.js';
import {useQuasar} from 'quasar'
import {useRoute, useRouter} from "vue-router";

const router = useRouter()
const route = useRoute()
const dataProductsStore = useDataProductsStore()
const notify = useNotify();
const $q = useQuasar()

// References
const fileInput = ref(null);
const folderInput = ref(null);

// Trigger file input click when button is clicked
const triggerFileInput = () => {
  fileInput.value.click();
};

// Trigger folder input click when button is clicked
const triggerFolderInput = () => {
  folderInput.value.click();
};

const triggerDDM = () => {
    router.push({ path: route.path.substring(0, route.path.lastIndexOf("/")) + "/DDM" })
};

// Handle file selection and read the file
const handleFileUpload = (event) => {
  const file_list = event.target.files;

  //Special case when using firefox and windows, where a csv file is interpreted as excel file type
  //const csvFirefoxWindowsImport = file && file.type === 'application/vnd.ms-excel' && file.name.split('.').pop() === 'csv'

  //if (file && (file.type === 'text/csv' || csvFirefoxWindowsImport) ) {
    console.log(file_list)
  if (file_list.length > 0) {
    sendFileToBackend(file_list);
  }
  else {
    notify.negative("No files selected (Maybe path too long?)")
  }
};

// Function to send the CSV file to the backend
const sendFileToBackend = async (file_list) => {
  const formData = new FormData();
  for (let i = 0; i < file_list.length; i++) {
        formData.append("files", file_list[i]);
    }

  try {
    $q.loading.show({message: 'Creating data product...'})
    const response = await odinApi.post('/data-products', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    $q.loading.hide()

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
