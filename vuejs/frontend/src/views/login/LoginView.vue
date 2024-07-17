<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import qs from 'qs';

const defaultErrorMessage = "LoginView.vueでエラー"
const DJANGO_BASEURL = process.env.VUE_APP_API_BASE_URL;
const id = ref('');
const pw = ref('')
const message = ref('ログインして下さい')
const visible = ref(false)
/**
 * ログイン認証処理
 */
const login = async () => {
    const REQUESTURL = `${DJANGO_BASEURL}/accounts/login/`
    const data = qs.stringify({ user_id: id.value, password: pw.value })/**クエリストリングの生成 （シリアライズ＝直列化）*/

    const {error,token,user_id,statusmessage} = await axios.post(REQUESTURL, data)
    .then(e => {
        const d = e.data;
        return {error:d.error,token:d.token,user_id:d.user_id,message:d.detail}
    }
    ).catch(e => {
        console.error(defaultErrorMessage,e)
        return {error:e.response.status,message:'認証に失敗しました。'}
    })
    message.value = statusmessage;
    
    
    //error なし
    if(error == 0){
        //認証情報をセッションストレージに格納
        sessionStorage.clear();//セッションストレージをクリアする
        sessionStorage.setItem('user_id', user_id)
        sessionStorage.setItem('user_token', token)
        window.location = '/tree'
    }else{
        alert(statusmessage)
    }
    
}
/**
 * マウント時の処理
 */
onMounted(() => {
});
</script>
<template>
    <div>
        <v-img class="mx-auto my-6" max-width="228"
            src="https://cdn.vuetifyjs.com/docs/images/logos/vuetify-logo-v3-slim-text-light.svg"></v-img>

        <v-card class="mx-auto pa-12 pb-8" elevation="8" max-width="448" rounded="lg">
            <div class="text-subtitle-1 text-medium-emphasis">Account</div>

            <!-- ID -->
            <v-text-field density="compact" placeholder="Email address" prepend-inner-icon="mdi-email-outline"
                variant="outlined" v-model="id" tabindex="1"></v-text-field>

            <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
                Password

                <a class="text-caption text-decoration-none text-blue" href="#" rel="noopener noreferrer"
                    target="_blank">
                    Forgot login password?</a>
            </div>
            <!-- PassWord -->
            <v-text-field :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'" :type="visible ? 'text' : 'password'"
                density="compact" placeholder="Enter your password" prepend-inner-icon="mdi-lock-outline"
                variant="outlined" @click:append-inner="visible = !visible" v-model="pw" tabindex="5"></v-text-field>

            <v-card class="mb-12" color="surface-variant" variant="tonal">
                <v-card-text class="text-medium-emphasis text-caption">
                    {{ message }}
                </v-card-text>
            </v-card>

            <!--Login Button -->
            <v-btn class="mb-8" color="blue" size="large" variant="tonal" block @click="login" tabindex="10">
                Log In
            </v-btn>

            <v-card-text class="text-center">
                <a class="text-blue text-decoration-none" href="#" rel="noopener noreferrer" target="_blank">
                    Sign up now <v-icon icon="mdi-chevron-right"></v-icon>
                </a>
            </v-card-text>
        </v-card>
    </div>
</template>
<style scoped></style>