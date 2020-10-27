import Vue from 'vue'
import App from './App.vue'
import router from './router'

let host = window.location.origin.split(':');
let ws_port = ':8828';
if(host.length > 2){
    host.pop()
}
host = host.join(':');

Vue.config.productionTip = false;
Vue.prototype.api_host =  host + ws_port;
Vue.prototype.api_list = {
  'login':'/login',
  'room_list':'/room_list'
}
new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

// Vue.prototype.ws =  new WebSocket('ws://localhost:8000/test');
