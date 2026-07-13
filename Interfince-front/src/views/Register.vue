<template>
    <p class="page-container">正在跳转到登录页...</p>
</template>

<script>
    export default {
        name: "Register",
        mounted() {
            this.$router.push('/login');
        }
    }
</script>

<style scoped>
    .page-container {
        font-size: 20px;
        text-align: center;
        color: rgb(192, 204, 218);
    }
</style>
