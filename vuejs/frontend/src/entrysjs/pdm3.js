import { createApp } from 'vue'
import App from '@/views/pdm3/IndexView.vue'
import router from '@/router/pdm3'
//import store from '@/store/tree'
import vuetify from '@/plugins/vuetify'
import { loadFonts } from '@/plugins/webfontloader'

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .mount('#app')

