import Vue from 'vue'
import App from './App.vue'
import router from './router'

Vue.config.productionTip = false
new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

// Vue.prototype.ws =  new WebSocket('ws://localhost:8000/test');
