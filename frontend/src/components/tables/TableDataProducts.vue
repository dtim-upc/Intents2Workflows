<template>
    <div class="q-pa-md">
      <q-table :rows="dataProductsStore.dataProducts" :columns="columns" :filter="search" row-key="id"
               no-results-label="The filter didn't uncover any results">
  
        <template v-slot:top-left="">
          <div class="q-table__title">
            Data products
          </div>
        </template>
  
        <template v-slot:top-right="props">
  
          <q-input outlined dense debounce="400" color="primary" v-model="search">
            <template v-slot:append>
              <q-icon name="search"/>
            </template>
          </q-input>
  
          <FullScreenToggle :props="props" @toggle="props.toggleFullscreen"/>
        </template>
  
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn dense round flat color="grey" @click="deleteRow(props)" icon="delete"></q-btn>
          </q-td>
        </template>

        <template v-slot:no-data>
          <div class="full-width row flex-center text-accent q-gutter-sm q-pa-xl" style="flex-direction: column">
            <NoDataImage/>
            <span style="color: rgb(102, 102, 135);font-weight: 500;font-size: 1rem;line-height: 1.25;">No data products.</span>
          </div>
        </template>
  
      </q-table>

      <EditDataProductForm v-model:show="showEditDataProduct" :dataProductData="selectedDataProduct" />
  
      <ConfirmDialog v-model:show="showConfirmDialog" title="Confirm deletion of a data product" 
                      body="Do you really want to delete the data product?"
                      :onConfirm="confirmDelete"/>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref} from "vue";
  import {useDataProductsStore} from 'src/stores/dataProductsStore.js'
  import NoDataImage from "src/assets/NoDataImage.vue";
  import ConfirmDialog from "src/components/utils/ConfirmDialog.vue";
  import EditDataProductForm from "src/components/forms/EditDataProductForm.vue";
  import FullScreenToggle from "./TableUtils/FullScreenToggle.vue";
  
  const dataProductsStore = useDataProductsStore()
  
  const selectedDataProduct = ref(null)
  
  const search = ref("")
  
  const showConfirmDialog = ref(false)
  const showEditDataProduct = ref(false)

  const columns = [
    {name: "fileName", label: "Name", align: "center", field: "name", sortable: true},
    {name: "size", label: "Size (MB)", align: "center", field: "size", sortable: true},
    {name: "uploadTime", label: "Upload time", align: "center", field: "creation_date", sortable: true},
    {name: 'actions', label: 'Actions', align: 'center', field: 'actions', sortable: false,},
  ]

  onMounted(async() => {
    await dataProductsStore.getDataProducts()
  })
  
  let confirmDelete = () => {}
  const deleteRow = (propsRow) => {
    console.log(propsRow.row)
    showConfirmDialog.value = true
    confirmDelete = () => {
        dataProductsStore.deleteDataProduct(propsRow.row.name)
    }
  }
  
  const editRow = (propsRow) => {
    showEditDataProduct.value = true
    selectedDataProduct.value = propsRow.row
  }
  </script>
  