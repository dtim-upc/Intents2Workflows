<template>
  <q-card class="q-pa-md" style="height: 100vh; display: flex; flex-direction: column; position: relative;">
    <!-- Header -->
    <q-card-section>
      <div class="text-h6 q-mb-sm">Import files from DDM</div>
      <div class="q-mb-md text-subtitle2 text-grey-7">
        Browse the file tree below and select an file or folder to import.
      </div>
    </q-card-section>

    <!-- Show loading spinner while fetching data -->
    <q-card-section v-if="loading" class="q-pa-none" style="display: flex; justify-content: center; align-items: center; flex: 1 1 auto;">
      <q-spinner color="primary" size="50px" />
    </q-card-section>

    <!-- Scrollable tree -->
    <q-card-section class="q-pa-none" style="flex: 1 1 auto; overflow-y: auto; padding-bottom: 80px;">
      <!-- Add bottom padding to avoid footer overlap -->
      <q-tree
        :nodes="nodes"
        node-key="id"
        label-key="label"
        children-key="children"
        @lazy-load="onLazyLoad"
        selection="single"
        v-model:selected="selected"
        selected-color="blue-8"
        selected-bg-color="black-1"
        @update:selected="onSelect"
      />
    </q-card-section>

    <!-- Floating footer -->
    <div
      style="
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f5f5f5;
        padding: 16px;
        border-top: 1px solid #ccc;
        display: flex;
        justify-content: space-between;
        align-items: center;
      "
    >
      <div>
        Selected item: <strong>{{ selected_node?.label || 'None' }}</strong>
      </div>

      <!-- Checkbox and Upload Button -->
      <div class="q-gutter-md" style="display: flex; align-items: center;">
        <!-- Checkbox with description -->
        <q-checkbox
          v-model="tensorImport"
          label="Tensor import"
          dense
          color="primary"
          style="margin-right: 10px;"
          v-if="selected_node?.folder"
        />
      <q-btn
        label="Import"
        icon="cloud_download"
        color="primary"
        @click="downloadItem"
      />
      </div>
    </div>
  </q-card>
</template>





<script setup>
  import { ref, onMounted } from 'vue';
  import { QTree, useQuasar } from 'quasar';
  import FileSaver from 'file-saver';
  import { useNotify } from 'src/use/useNotify.js';
  import {odinApi} from 'boot/axios';
  import {useRoute, useRouter} from "vue-router";

  const router = useRouter()
  const route = useRoute()
  const $q = useQuasar()
  const notify = useNotify();

  const nodes = ref([])
  const selected = ref(null)
  const selected_node = ref(null)
  const loading = ref(true);  // Track loading state
  const tensorImport = ref(false)


  const bearerToken = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI1UFdHcVJMRjRDcDBkYTdLUFB4OWtMTVZDR2xYSmh1MHpVWDY1Z3FlSDVJIn0.eyJleHAiOjE3NjY3NTQ2OTUsImlhdCI6MTc2NTg5MDY5NSwianRpIjoiNmE3ZGFmMzctOGIzMC00MmEwLTkwNWYtMTUyMTllOWIxMzViIiwiaXNzIjoiaHR0cHM6Ly9leHRyZW1leHAtYXV0aDAxLnRibS50dWRlbGZ0Lm5sL2F1dGgvcmVhbG1zL2V4dHJlbWV4cCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI1NjM5NTJiZC1mZTkzLTQ2OTktOWI5MC1mYTdiZjU2Njk1YzUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhY2Nlc3Njb250cm9sIiwic2Vzc2lvbl9zdGF0ZSI6IjVlMDZmOGU0LTA4NTMtNDI5ZS1iMjBjLWE0N2RlNTBiNjcyYiIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1leHRyZW1leHAiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6IjVlMDZmOGU0LTA4NTMtNDI5ZS1iMjBjLWE0N2RlNTBiNjcyYiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiVVBDIERlbW8iLCJncm91cHMiOlsiZGVmYXVsdC1yb2xlcy1leHRyZW1leHAiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl0sInByZWZlcnJlZF91c2VybmFtZSI6InVwY2RlbW8iLCJsb2NhbGUiOiJlbiIsImdpdmVuX25hbWUiOiJVUEMiLCJmYW1pbHlfbmFtZSI6IkRlbW8iLCJlbWFpbCI6ImRlbW9AdXBjLmVkdSJ9.e_CcjKPi_EO_QUuMyL2ZrHD2fBy3wkPPq6GXCv8o54VzA5ttR_in2pyPLSzTbvc8qkJlzZTJHIMxT_02MLKFJ7VTac05b6Rhl1jxPx53lZ0lR-DI2SLcmE3BeLgNAr-BBRId52ILYDc276Rl_ecs48Bm47v4JZfBg96hW4J0DMOoEQ3qKu8td5mJHy1Yke5pxySJE76rpSUS17vqH40JgfZ3VDsygp63veqCKKvFqg0Ffm6ku9-8_T8PoSAnC4nt6J9MMW8lGg3YWiOryxJRnvxlSEB8vTN285EwcPv4VK1IJZWp26Re6n3vzAm2ibrWXaPd3wiROjE5G3TUdtXrHw'; // Replace this with the actual token

  const fileColors = {
  pdf: 'red-6',
  csv: 'green-6',
}


  const mapApiNode = (item) => {
    const mapped = {
      id: item.key,
      label: item.data.name,
      children: !item.leaf ? [] : null,
      lazy: !item.leaf,
      icon: item.data.type == 'folder' ? 'folder': 'description',
      iconColor: item.data.type == 'folder' ? 'orange-8' : fileColors[item.data.type] ?? 'grey-7',
      path: item.data.type == 'folder'? item.data.path : item.data.path + '/' + item.data.name,
      folder: item.data.type == 'folder',
      format: item.data.type
    }
    return mapped
  }


  const fetchChildren = async (parentId) => {
    const data  = await getFiles(parentId)
    const mapping = data.map(mapApiNode)
    return mapping
  }

  // Initial root load
  onMounted(async () => {
    nodes.value = await fetchChildren("")
    loading.value = false; 
  })

  // Lazy loader
  const onLazyLoad = async ({ node, done, fail }) => {
    try {
      const children = await fetchChildren(node.id)
      done(children)
    } catch (err) {
      console.error(err)
      fail()
    }
  }


  const getFiles = async (parent) => {
    const apiUrl = 'https://ddm.extremexp-icom.intracom-telecom.com/ddm/catalog/tree?perPage=100&parent='+parent;
        // Helper function to add the Authorization header to the fetch request
    const getAuthHeaders = () => {
      return {
        'Authorization': `Bearer ${bearerToken}`,
        'Content-Type': 'application/json'
      };
    };
    try {
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: getAuthHeaders() // Add the Authorization header
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const data = await response.json();
      return data.nodes

    } catch (error) {
      console.error('Error fetching file system data:', error);
    }
  }

   const downloadProject = async (id) => {
        // Helper function to add the Authorization header to the fetch request
    const fileUrl = 'https://ddm.extremexp-icom.intracom-telecom.com/ddm/files/download/project';
    const getAuthHeaders = () => {
      return {
        'Authorization': `Bearer ${bearerToken}`,
        'Content-Type': 'application/json'
      };
    };
    try {
      const response = await fetch(fileUrl, {
        method: 'POST',
        headers: getAuthHeaders(), // Add the Authorization header
        body: `{"project_id": "${id}"}`,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      return await response.blob()
      return new Blob([text], { type: 'text/plain' })

    } catch (error) {
      console.error('Error fetching file system data:', error);
    }
  }

  const donwnloadFile = async (id) => {
        // Helper function to add the Authorization header to the fetch request
    const fileUrl = `https://ddm.extremexp-icom.intracom-telecom.com/ddm/file/${id.replace("file-","")}`;
    const getAuthHeaders = () => {
      return {
        'Authorization': `Bearer ${bearerToken}`,
        'Content-Type': 'application/json'
      };
    };
    try {
      const response = await fetch(fileUrl, {
        method: 'GET',
        headers: getAuthHeaders(), // Add the Authorization header
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      return await response.blob()

    } catch (error) {
      console.error('Error fetching file system data:', error);
    }
  }

  const downloadItem = async() => {

    if (selected_node?.value?.folder) {

      $q.loading.show({message: 'Downloading'})
      try {
        const response = await downloadProject(selected_node?.value?.path);
        $q.loading.hide()
        sendFileToBackend([new File([response], selected_node.value.label+'.zip', { type: response.type })],tensorImport.value)
        router.push({ path: route.path.substring(0, route.path.lastIndexOf("/")) + "/data-products" })
        //var decodedString = atob(response);
        //FileSaver.saveAs(response, 'test.zip')
      } catch (error) {
          console.error("Error:", error);
          $q.loading.hide()
      }
    }
    else {
      if (!selected_node?.value?.folder) {
        try {
          $q.loading.show({message: 'Downloading'})
          const response = await donwnloadFile(selected_node?.value?.id)
          //FileSaver.saveAs(response, selected_node.value.label)
          $q.loading.hide()
          sendFileToBackend([new File([response], selected_node.value.label, { type: response.type })])
          router.push({ path: route.path.substring(0, route.path.lastIndexOf("/")) + "/data-products" })
        }
          catch (error) {
          console.error("Error:", error);
          $q.loading.hide()
      }
      }
      else{
        console.log("Undefined selection")
      }

    }
}


const findNodeById = (list, id) => { 
  for (const node of list) { 
    if (node.id === id) 
      return node 
    if (node.children?.length) { 
      const found = findNodeById(node.children, id) 
      if (found) return found 
    } 
  } 
  return null }

const onSelect = (id) => {
  selected.value = id
  selected_node.value = findNodeById(nodes.value, id)
  tensorImport.value = false
  console.log("Selected node:",selected_node)
}


const sendFileToBackend = async (file_list, tensor=false) => {
  const formData = new FormData();
  for (let i = 0; i < file_list.length; i++) {
        formData.append("files", file_list[i]);
    }
    formData.append("tensor",tensor)

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
    console.error(error)
    $q.loading.hide()
  }

}
</script>
