import { defineStore } from 'pinia';
import { useNotify } from 'src/use/useNotify.js';
import dataProductAPI from "src/api/dataProductsAPI";
import { LocalStorage } from 'quasar'


const notify = useNotify();

export const useDdmStore = defineStore('ddm', {
  state: () => ({
    user: LocalStorage.getItem('user'),
    token: LocalStorage.getItem('token'),
    userid: LocalStorage.getItem('userid'),
    experiment: null
  }),

  getters: {
  showLoginDialog: (state) => !state.token,
  isLogged: (state) => state.token
  },

  actions: {
    async login(username, password) { //DDM Login
      try {
        const response = await dataProductAPI.getDDMToken({'username':username, 'password':password});
        this.token = response.data.token;
        this.userid = response.data.id
        this.user = username
        
        LocalStorage.setItem('user', this.user),
        LocalStorage.setItem('token', this.token),
        LocalStorage.setItem('userid', this.userid)
      }catch (error) {
        notify.negative("Login error");
        console.error("Error:", error);
      }

    },
    async getExperimentName(experimentId) {
      try {
        const response = await dataProductAPI.getExperimentName(experimentId, this.token)
        this.experiment = response.data.experimentName
      }catch (error) {
        notify.negative("Error getting experiment name");
        console.error("Error:", error);
      }
    }
  }
});



