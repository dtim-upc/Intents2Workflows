import { defineStore } from 'pinia';
import { useNotify } from 'src/use/useNotify.js';
import axios from 'axios'

const notify = useNotify();

export const useDdmStore = defineStore('ddm', {
  state: () => ({
    user: "",
    token: "",
  }),

  actions: {
    async login(username, password) { //DDM Login
      try {
        const response = await axios.post('/ddm/login',{'username':username, 'password':password});
        this.token = response.data.access_token;
        this.user = username
      }catch (error) {
        notify.negative("Login error");
        console.error("Error:", error);
      }

    },
  }
});



