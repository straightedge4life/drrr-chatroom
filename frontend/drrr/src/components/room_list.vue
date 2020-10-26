<template> 
<div>
    <div class="userinfo-nav">
        <div class="avatar nav-item">
            <img :src="require('../assets/avatars/icon_'+avatar_map[avatar_id]+'.png')" alt="">
        </div>
        <div class="username nav-item">{{nickname}}</div>
        <span class="exit-btn" v-on:click="exit()">EXIT!</span> 
    </div>

    <div class="room-list">
        <div class="list-title">
            <span>ROOM LIST</span>
        </div>

        <div class="room-list-info">
            <span class="online-num">Online: (<span>{{ online_user }}</span>)</span>
            <input type="submit" class="create-btn" value="CREATE ROOM" v-on:click="go_to('/room/create')">
        </div>

        <ul class="room-item" v-for="room in this.room_list" :key="room.pk">
            <li>
                <span class="room-title">{{ room.name }}</span>
                <span class="room-host">{{ room.host_nickname }}</span>
                <span class="room-online-num">{{ room.curr_member }}/{{ room.max_member }}</span>
                <input type="submit" class="create-btn room-enter" value="JOIN" v-on:click="go_to('/room/'+room.id)">
            </li>

           

         
        </ul>
    </div>
</div>
</template>

<style>
    @import url('../assets/css/roomlist.css');
</style>

<script>
import axios from '../assets/js/axios'
import ws from '../assets/js/websocket'

export default {
    data(){
        return {
            uuid:localStorage.getItem('uuid'),
            nickname:localStorage.getItem('nickname'),
            avatar_id:localStorage.getItem('avatar_id'),
            avatar_map:{
                1:'gg',
                2:'kanra',
                3:'setton',
                4:'tanaka',
                5:'zaika',
                6:'zawa'
            },
            room_list:[],
            online_user:0
        }
    },
    created() {
        // window.addEventListener('beforeunload', e => this.beforeUnload(e));
        // 未登陆
        if(this.uuid == undefined){
            this.$router.push('/login');
        }

        let that = this;
    
        let t = setInterval(function(){
            if(ws.readyState == 1){
                that.bind_user(ws,that.uuid);
                ws.onmessage = that.onmessage;
                that.get_online_user(ws)
                window.clearInterval(t)
            }
        },100);


        this.get_room_list()
        
       
    },
    
    mounted:function(){},
    
    methods:{
        main:function(ws){
            this.bind_user(ws, this.uuid);
            ws.onmessage = this.onmessage;
        },
        bind_user:function(ws, uuid){
            ws.send(JSON.stringify({type:'bind', uuid:uuid}));
        },
        onmessage:function(e){
            let data = JSON.parse(e.data);
                console.log('recev msg');
                console.log(data);
                if(data.type == 'system'){
                   switch(data.content){
                       case 'room_list':
                           this.get_room_list();
                           break;
                        case 'online_user':
                            this.online_user = data.data
                            break;
                        default:
                            // do nothing by now...
                   }
                }
        },
        go_to:function(uri){
            this.$router.push(uri)
        },
        get_room_list(){
            let that = this;
             axios({
                method:'POST',
                url:'http://localhost:8828/room_list',
                data:{
                    uuid:this.uuid,
                }
                })
            .then(function(response){
                // console.log(response)
                if(response.data.status == 'SUCCESS'){
                    that.room_list = response.data.data
                }else{
                    // 异常处理
                }
            })
        },
        get_online_user(ws){
            ws.send(JSON.stringify({type:'get_online_user'}));
        },
        exit:function(){
            ws.send(JSON.stringify({type:'exit_user'}));
            localStorage.removeItem('uuid');
            this.go_to('/login')
        },
        
    }
}
</script>