<template>
    <div class="container">
        <span>
            Here is Home Page
        </span>
        <br>
        <button v-on:click="go_to_login()">跳转</button>
    </div>
</template>

<style>
    .container{
        background-color:red;
    }
</style>
<script>
export default {
    data(){
        return{
           
        }
    },
    methods:{
        go_to_login(){
            this.$router.push('/login')
        }
    }
}

</script>