<template>
  <DDMLogin v-model="isLoginVisible"/>
  <q-card class="q-pa-md" style="height: 100vh; display: flex; flex-direction: column; position: relative;">
    <!-- Header -->
    <q-card-section>
      <div class="text-h6 q-mb-sm">Import files from DDM</div>
      <div class="q-mb-md text-subtitle2 text-grey-7">
        Browse the file tree below and select a file or folder to import.
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
  import { ref, onMounted, watch, nextTick } from 'vue';
  import { QTree, useQuasar } from 'quasar';
  import { useNotify } from 'src/use/useNotify.js';
  import { odinApi } from 'boot/axios';
  import { useRoute, useRouter } from "vue-router";
  import { useDdmStore } from 'src/stores/ddmStore';
  import DDMLogin from "src/components/utils/DDMLogin.vue";

  const ddmStore = useDdmStore();
  const router = useRouter();
  const route = useRoute();
  const $q = useQuasar();
  const notify = useNotify();

  const nodes = ref([]);
  const selected = ref(null);
  const selected_node = ref(null);
  const loading = ref(true);  // Track loading state
  const tensorImport = ref(false);
  const isLoginVisible = ref(false);

  var bearerToken = "";

  const fileColors = {
    pdf: 'red-6',
    csv: 'green-6',
  };

  // Map API response to tree structure
  const mapApiNode = (item) => {
    const mapped = {
      id: item.key,
      label: item.data.name,
      children: !item.leaf ? [] : null,
      lazy: !item.leaf,
      icon: item.data.type == 'folder' ? 'folder' : 'description',
      iconColor: item.data.type == 'folder' ? 'orange-8' : fileColors[item.data.type] ?? 'grey-7',
      path: item.data.type == 'folder' ? item.data.path : item.data.path + '/' + item.data.name,
      folder: item.data.type == 'folder',
      format: item.data.type
    };
    return mapped;
  };

  // Fetch children files/folders
  const fetchChildren = async (parentId) => {
    const data = await getFiles(parentId);
    const mapping = data.map(mapApiNode);
    return mapping;
  };

  // Lazy loader to fetch children dynamically
  const onLazyLoad = async ({ node, done, fail }) => {
    try {
      const children = await fetchChildren(node.id);
      done(children);
    } catch (err) {
      console.error(err);
      fail();
    }
  };

  // Watch for login status changes and react accordingly
  watch(() => ddmStore.token, async (newToken) => {
    if (newToken) {
      bearerToken = newToken;
      nodes.value = await fetchChildren(""); // Re-fetch data if token changes
    }
  });

  // Initial mount: check if already logged in
onMounted(async () => {
  bearerToken = ddmStore.token;
  if (bearerToken) {
    isLoginVisible.value = false;  // If logged in, hide the login
    nodes.value = await fetchChildren("");
  } else {
    isLoginVisible.value = true;  // If no token, show login dialog
  }
  loading.value = false;  // Set loading to false after data has been processed
});

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

    if (!ddmStore.token) {
      isLoginVisible.value = true;
      return
    }

    if (selected_node?.value?.folder) {

      $q.loading.show({message: 'Downloading'})
      try {
        const response = await downloadProject(selected_node?.value?.path);
        $q.loading.hide()
        await sendFileToBackend([new File([response], selected_node.value.label+'.zip', { type: response.type })],tensorImport.value,selected_node.value.path)
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
          await sendFileToBackend([new File([response], selected_node.value.label, { type: response.type })],false, selected_node.value.path)
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


const sendFileToBackend = async (file_list, tensor=false, path=null) => {
  const formData = new FormData();
  for (let i = 0; i < file_list.length; i++) {
        formData.append("files", file_list[i]);
    }
    formData.append("tensor",tensor)
    formData.append("original_path", path)

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
