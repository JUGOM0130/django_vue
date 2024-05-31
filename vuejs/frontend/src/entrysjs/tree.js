import { createApp } from 'vue'
import App from '@/views/tree/TreeMenu.vue'
import router from '@/router/tree'
import store from '@/store/tree'
import vuetify from '@/plugins/vuetify'
import { loadFonts } from '@/plugins/webfontloader'

loadFonts()

createApp(App)
  .use(router)
  .use(store)
  .use(vuetify)
  .mount('#app')
