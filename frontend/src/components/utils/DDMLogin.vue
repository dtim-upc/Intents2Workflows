<template>
  <div>
    <q-dialog :model-value="ddmStore.showLoginDialog" persistent> <!--@hide="onDialogClose"-->
      <q-card 
        class="q-pa-lg rounded-borders border shadow-2 custom-card-padding card-width">

        <!-- Header -->
        <q-card-section class="flex column items-center q-pa-xs">
          <img src="assets/logo-carre.png" alt="Logo" style="width: 80px; margin-bottom: 4px;" />
          <h3 class="login-title" style="font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 600; color:#4b5563; margin: 0;">
              Login to ExtremeXP
          </h3>
        </q-card-section>

        <!-- Username -->
        <q-card-section class="q-pa-sm">
          <div>
            <!-- Label with user icon -->
            <div class="row items-center q-gutter-sm q-mb-xs">
              <i class="pi pi-user" style="color:#4b5563;"></i>
              <span style="font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 400; color:#4b5563; letter-spacing: -0.25px;">Username</span>
            </div>

            <!-- Username input field -->
            <q-input
              v-model="username"
              outlined
              dense
              hide-bottom-space
              class="w-full"
            />
          </div>
        </q-card-section>

        <!-- Password -->
        <q-card-section class="q-pa-sm">
          <div>
            <!-- Label with lock icon -->
            <div class="row items-center q-gutter-sm q-mb-xs">
              <i class="pi pi-lock" style="color:#4b5563;"></i>
              <span style="font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 400; color:#4b5563; letter-spacing: -0.25px;">Password</span>
            </div>

            <!-- Password input field -->
            <q-input
              v-model="password"
              type="password"
              outlined
              dense
              hide-bottom-space
              class="w-full"
            />
          </div>
        </q-card-section>

        <!-- Login Button -->
        <q-card-section class="q-pa-sm">
          <q-btn
            class="full-width q-btn-custom"
            unelevated
            aria-label="Login"
            @click="handleLogin"
          >
            <span class="btn-content">
              <i class="pi pi-sign-in" style="margin-right: 0.5em;"></i>
              <span>Login</span>
            </span>
          </q-btn>
        </q-card-section>

      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
  import { ref, watch, onMounted } from 'vue';
  import { useDdmStore } from 'src/stores/ddmStore';

  const ddmStore = useDdmStore();

  const username = ref('');
  const password = ref('');


  // Handle Login
  const handleLogin = async () => {

    if (ddmStore.token === '') {
      // Perform login
      await ddmStore.login(username.value, password.value);

      if (!ddmStore.token) {
        console.error('Login failed');
        // Handle login failure (e.g., show error message)
      }
    } else {
      console.log('Already logged in');
    }
  };

</script>


<style scoped>
.rounded-borders {
  border-radius: 5px; /* round corners */
}

.card-width {
    max-width: 600px
}

.custom-card-padding {
  padding-top: 44px;     /* top padding */
  padding-bottom: 44px;  /* bottom padding */
  padding-left: 44px;    /* increased lateral padding */
  padding-right: 44px;   /* increased lateral padding */
}

.q-btn-custom {
  text-transform: none;
  padding: 0.6em 0.6em; /* adjust vertical/horizontal padding */
  background-color: #3b82f6;  /* your custom color */
  color: #ffffff;             /* text color */
}

.q-btn-custom i.pi {
  font-size: 16px; /* adjust icon size */
}

/* Flex container for icon + text */
.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;   /* centers the text horizontally */
  position: relative;
  width: 100%;
}

/* Icon positioned absolutely on the left */
.btn-content i.pi {
  position: absolute;
  left: 0.6em;               /* match horizontal padding */
  font-size: 16px;
}

/* Text remains centered */
.btn-content span {
  flex: 1;
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 625;
}

</style>