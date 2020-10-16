import Vue from 'vue'
import VueRouter from 'vue-router'
import RoomList from '../components/room_list.vue'
import Login from '../components/login.vue'
import Home from '../components/home.vue'
import RoomCreate from '../components/room_create.vue'
import Room from '../components/room.vue'
Vue.use(VueRouter)

  const routes = [
  // {
  //   path: '/',
  //   name: 'Home',
  //   component: Home
  // },
  // {
  //   path: '/about',
  //   name: 'About',
  //   // route level code-splitting
  //   // this generates a separate chunk (about.[hash].js) for this route
  //   // which is lazy-loaded when the route is visited.
  //   component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  // }
  {
    path:'/',
    name:'home',
    component:Home
  },
  {
    path: '/room_list',
    name:'Room List',
    component:RoomList
  },
  {
    path:'/login',
    name:'Login',
    component:Login
  },
  {
    path:'/room/create',
    name:'RoomCreate',
    component:RoomCreate
  },
  {
    path:'/room/:id',
    name:'Room',
    component:Room
  },
]

const router = new VueRouter({
  routes
})
export default router
