import { createApp } from 'vue'
import App from '@/components/IndexView.vue'
import router from '@/c_tree/router'
//import store from '@/store/tree'
import vuetify from '@/plugins/vuetify'
import { loadFonts } from '@/plugins/webfontloader'

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .mount('#app')

