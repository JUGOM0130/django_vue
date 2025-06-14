import { createApp } from 'vue'
import App from '@/views/login/LoginView.vue'
import vuetify from '@/plugins/vuetify'
import router from '@/router/index'
import { loadFonts } from '@/plugins/webfontloader'

loadFonts()

createApp(App)
  .use(vuetify)
  .use(router)
  .mount('#app')
