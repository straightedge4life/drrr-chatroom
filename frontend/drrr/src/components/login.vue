<template>
    <div class="login-container">
        <div class="login logo-container">
            <img :src="dollars_logo_url">
        </div>

        <div class="login login-form">
            <label for="nickname">USERNAME:</label>
            <input type="text" name="nickname" id="nickname" v-model="nickname">
        </div>
        <span class="login login-btn" v-on:click="login()">ENTER</span>

        <div class="avatar-options-container">
            <span class="options-text">[ Avatars ]</span>
            <div 
            class="options-text sanjiao" 
            v-bind:class="[avatar_option_is_show ? 'sanjiao-show' : 'sanjiao-hide']"
            @click="avatar_option_is_show = !avatar_option_is_show"
            ></div> 
            <div 
            class="avatars-list"
            v-bind:class="[avatar_option_is_show? '' : 'hide']"
            >
                <ul>
                    <li 
                    v-for="avatar in this.avatar_urls" 
                    :key="avatar.img_url" 
                    v-bind:class="[avatar.id == selected_avatar_id ? 'avatars-seleted ' : '']" 
                    :avatar_id="avatar.id"
                    v-on:click="select_avatar(avatar.id)"
                    >
                        <img :src="avatar.img_url" alt="">
                    </li>
                </ul>
            </div>
        </div>

        <div class="mask" v-bind:class="{ 'display-none':tips_is_close }"></div>
        <div class="tips" v-bind:class="{ 'display-none':tips_is_close }">
            <div class="title">{{ tips_title}}</div>
            <div class="message">{{ tips_message}}</div>
            <div class="oper">
                <div class="button confirm" v-on:click="tips_close()">OK</div>
            </div>
        </div>
    </div>
</template>

<style>
    @import url('../assets/css/login.css');
    @import url('../assets/css/tips.css');
    
</style>


<script>
import axios from '../assets/js/axios'
import ws from '../assets/js/websocket'

export default {
    data(){
        return {
            login_api:1,
            tips_is_close:1,
            tips_title:'ERROR',
            tips_message:'Unknow error,please refresh your browser.',
            uuid:localStorage.getItem('uuid'),
            dollars_logo_url:require('../assets/dollars-logo.png'),
            avatar_urls:[
                {id:1,img_url:require('../assets/avatars/icon_gg.png')},
                {id:2,img_url:require('../assets/avatars/icon_kanra.png')},
                {id:3,img_url:require('../assets/avatars/icon_setton.png')},
                {id:4,img_url:require('../assets/avatars/icon_tanaka.png')},
                {id:5,img_url:require('../assets/avatars/icon_zaika.png')},
                {id:6,img_url:require('../assets/avatars/icon_zawa.png')},
            ],
            selected_avatar_id:1,
            avatar_option_is_show:false,
            nickname:"john due"     
        }
    },
    created(){
        if(this.uuid){
            this.go_to('/room_list');
        }
        
    },
    mounted:function(){
      
    },
    methods:{ 
        tips_close:function(){
            this.tips_is_close = 1;
        },
        bind_user:function(uuid){
            ws.send(JSON.stringify({type:'bind', uuid:uuid}));
        },
        select_avatar:function(id){
            this.selected_avatar_id = id
        },
        go_to:function(uri){
            this.$router.push(uri)
        },
        login:function(){
            let that = this
            axios({
                method:'POST',
                url:this.api_host + this.api_list.login,
                data:{
                    nickname:this.nickname,
                    avatar:this.selected_avatar_id
                }
            })
            .then(function(response){
                if(response.data.status == 'SUCCESS'){
                    localStorage.setItem('uuid',response.data.uuid);
                    localStorage.setItem('nickname',that.nickname);
                    localStorage.setItem('avatar_id',that.selected_avatar_id);
                    that.bind_user(response.data.uuid);
                    that.go_to('/room_list')
                }else{
                    that.tips_message = response.data.message;
                    that.tips_is_close = 0;
                    
                }
            })
        }
    }
}
</script>