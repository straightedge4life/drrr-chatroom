<template> 
<div>
    <div class="room-header">
        <div class="header-form">
    
            <div class="message">
                <textarea name="message-content" id="" cols="30" rows="10" class="message-content" v-model.trim="chat_message" @keydown.enter="message_post(chat_message)"></textarea>
            </div>

            <div class="message-post">
                <input type="submit" value="P O S T" class="message-post-btn" v-on:click="message_post(chat_message)">
            </div>
        </div>

        <span class="exit-btn" v-on:click="exit_room()">EXIT!</span>
    </div>

    <div class="chat-log">
        <ul v-for="message in this.messages" :key="message.id">
            <li class="chat-item user-message"   v-if="message.type == 'message'">
                <div class="chat-user">
                    <img :src="require('../assets/avatars/icon_'+avatar_map[message.avatar]+'.png')" alt="">
                    <div>{{message.nickname}}</div>
                </div>

                <div :class="'chat-content '+avatar_map[message.avatar]">
                    <span>{{message.content}}</span>
                </div>
            </li>

            <li class="chat-item system-message" v-else>
                 —— —— <span>{{ message.content }}</span>
            </li>
        </ul>
    </div>
</div>

</template>

<style>
    @import url('../assets/css/room.css');
</style>

<script>
import ws from '../assets/js/websocket'

export default {
    data(){
        return{
            uuid:localStorage.getItem('uuid'),
            avatar_map:{
                1:'gg',
                2:'kanra',
                3:'setton',
                4:'tanaka',
                5:'zaika',
                6:'zawa'
            },
            room_id:this.$route.params.id,
            gg_avatar_urls:require('../assets/avatars/icon_gg.png'),
            kanra_avatar_urls:require('../assets/avatars/icon_kanra.png'),
            chat_message:'',
            messages:[]
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
                that.bind_user(ws, that.uuid);
                that.join_room(ws, that.uuid, that.room_id);
                ws.onmessage = that.onmessage;
                window.clearInterval(t)
            }
        },100);
        
        console.log(ws);
        // ws.onopen = function(){
        //     console.log('onopen');
        //     that.bind_user(ws, that.uuid);
        //     that.join_room(ws, that.uuid, that.room_id);
        //     ws.onmessage = that.onmessage;
        // };
        // if(this.ws == undefined || this.ws.readyState != this.ws.OPEN){
        //     console.log('刷新重连');
        //     let ws_con = new WebSocket('ws://localhost:8000/test');
        //     ws_con.onopen = function(){
        //         that.ws = ws_con;
        //         that.bind_user(that.ws, that.uuid);
        //         that.join_room(that.ws, that.uuid, that.room_id)
        //         that.ws.onmessage = that.onmessage;
        //     };
        // }else{
        //     //this.bind_user(this.ws, this.uuid);
        //     this.join_room(this.ws, this.uuid, this.room_id)
        //     this.ws.onmessage = this.onmessage;
        // }

     
    },
    mounted:function(){},
    destroyed(){
        // window.removeEventListener('beforeunload', e => this.beforeUnload(e));
    },
    methods:{
        join_room:function(ws, uuid, room_id){
            ws.send(JSON.stringify({type:'join', uuid:uuid, room_id:room_id}))
        },
        bind_user:function(ws, uuid){
            ws.send(JSON.stringify({type:'bind', uuid:uuid}));
        },
        onmessage:function(e){
            let data = JSON.parse(e.data);
            console.log(data);
            if(data.type == 'message' || data.type == 'notify'){
                this.messages.unshift(data);
            }else if(data.type == 'error'){
                this.go_to('/room_list');
            }else{
                // system
            }
                
        },
        go_to:function(uri){
            this.$router.push(uri)
        },
        message_post:function(message){
            ws.send(JSON.stringify({type:'message', uuid:this.uuid, content:this.chat_message}))
            
            this.chat_message = "";
        },
        exit_room:function(){
            ws.send(JSON.stringify({type:'exit', uuid:this.uuid}))
            this.go_to('/room_list')
        },
        beforeUnload:function(){
            // this.ws.close();
        },
    }
}
</script>