<template>
    <div>
        <div class="creation-title room-creation">
            ROOM CREATION
        </div>
        <div class="room-max-num">
            <input type="text" name="room-name" class="room-title" v-model.trim="room_name">
            <select name="room-num" class="room-num" v-model.trim="room_max_member ">
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8</option>
                <option value="9">9</option>
                <option value="10">10</option>
            </select>
        </div>
        <div class="room-creation creation-submit">
            <input type="submit" value="CREATE" class="creation-submit-btn" v-on:click="room_create()">
        </div>
    </div>
</template>

<style>

.room-creation{
    width:30rem;
}

.creation-title{
    margin: 10rem auto 1rem;
    color:white;
    text-align: center;
}


.room-max-num{
    width: 15.3rem;
    margin: 1rem auto;
}

.room-title{
    width:15rem;
    font-size:1.2rem;
    border-radius: 0.3rem;
}
.room-num{
    width: 3rem;
    font-size: 1.2rem;
    border:0;
    margin-left:-3.1rem;
}

.creation-submit{
    margin:1rem auto;
}

.creation-submit-btn{
    background-color: black;
    color: white;
    border: 0.18rem solid white;
    font-size: 0.9rem;
    font-weight: 700;
    width: 10rem;
    height: 2.2rem;
    text-align: center;
    border-radius: 1rem;
    font-family: 'Microsoft Yahei';
    margin:0 auto;
    display: block;
}

@media (max-width:570px) {
    .room-creation{
        width:100%;
    }
}


</style>
<script>
import ws from '../assets/js/websocket'

export default {
    data(){
        return {
            uuid:localStorage.getItem('uuid'),
            room_name:'',
            room_max_member:2
        }
    },
    created(){
        // window.addEventListener('beforeunload', e => this.beforeUnload(e));

        // 未登陆
        if(this.uuid == undefined){
            this.$router.push('/login');
        }

        let that = this;
        let t = setInterval(function(){
            if(ws.readyState == 1){
                that.bind_user(ws, that.uuid);
                ws.onmessage = that.onmessage;
                window.clearInterval(t)
            }
        },100);
        
        // this.bind_user(ws, this.uuid);
        // ws.onmessage = this.onmessage;

        // if(this.ws == undefined || this.ws.readyState != this.ws.OPEN){
        //     console.log('刷新重连');
        //     let ws_con = new WebSocket('ws://localhost:8000/test');
        //     ws_con.onopen = function(){
        //         that.ws = ws_con;
        //         that.bind_user(that.ws, that.uuid);
        //         that.ws.onmessage = that.onmessage;
        //     }
        // }else{
        //     //this.bind_user(this.ws, this.uuid);
        //     this.ws.onmessage = this.onmessage;
        // }
    },
    mounted:function(){},
    destroyed(){
        // window.removeEventListener('beforeunload', e => this.beforeUnload(e));
    },
    methods:{
        bind_user:function(ws, uuid){
            ws.send(JSON.stringify({type:'bind', uuid:uuid}));
        },
        onmessage:function(e){
            let data = JSON.parse(e.data);
            console.log(data);
            if(data.type == 'room_create' && data.status == 'success'){
                this.go_to('/room/' + data.room_id);
            }
        },
        go_to:function(uri){
            this.$router.push(uri)
        },
        room_create(){
            ws.send(JSON.stringify({
                type:'create', 
                uuid:this.uuid,
                name:this.room_name,
                max_member:this.room_max_member
            }))
        },
        beforeUnload:function(){
            // this.ws.close();
        },
    }
}
</script>