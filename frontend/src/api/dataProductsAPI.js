import {odinApi} from 'boot/axios';

export default {
  getDataProducts() {
    return odinApi.get('/data-products')
  },  
/*   materializeDataProduct(projectID, dataProductID) {
    return odinApi.post('/project/' + projectID + '/data-product/' + dataProductID + '/materialize')
  }, */
/*   postDataProduct(projectID, data) {
    return odinApi.post('/project/' + projectID + '/data-products', data)
  }, */
  deleteDataProduct(fileName) {
    return odinApi.delete('/data-products/' +  fileName)
  },
/*   putDataProduct(projectID, dataProductID, data) {
    return odinApi.put('/project/' + projectID + '/data-product/' +  dataProductID, data)
  }, */
/*   downloadTemporalDataProduct(projectID, dataProductUUID) {
    return odinApi.post('/project/' + projectID + '/download-temporal-data-product/' +  dataProductUUID)
  }, */
  downloadDataProduct(fileName) {
    return odinApi.get('/data-products/' +  fileName)
  },
  getDataProductAnnotations(fileName,data) {
    return odinApi.post('/data-products/' +  fileName + '/annotations',data)
  },
}
