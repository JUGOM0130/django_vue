import { createApp } from 'vue'
import App from './IndexView.vue'
import router from './router'
//import store from '@/store/tree'
import vuetify from '@/plugins/vuetify'
import { loadFonts } from '@/plugins/webfontloader'

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .mount('#app')

