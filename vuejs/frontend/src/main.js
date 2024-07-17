import { createApp } from 'vue'
import App from './views/login/LoginView.vue'
import router from './router/index'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .mount('#app')
