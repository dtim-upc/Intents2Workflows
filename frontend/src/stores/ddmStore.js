import { defineStore } from 'pinia';
import { useNotify } from 'src/use/useNotify.js';
import axios from 'axios'
import dataProductAPI from "src/api/dataProductsAPI";

const notify = useNotify();

export const useDdmStore = defineStore('ddm', {
  state: () => ({
    user: "",
    token: "",
  }),

  actions: {
    async login(username, password) { //DDM Login
      try {
        const response = await dataProductAPI.getDDMToken({'username':username, 'password':password});
        this.token = response.data.token;
        this.user = username
      }catch (error) {
        notify.negative("Login error");
        console.error("Error:", error);
      }

    },
  }
});



