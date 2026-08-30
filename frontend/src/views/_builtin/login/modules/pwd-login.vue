<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';
// import { loginModuleRecord } from '@/constants/app';
import { useAuthStore } from '@/store/modules/auth';
// import { useRouterPush } from '@/hooks/common/router';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { fetchCaptcha } from '@/service/api';
import { $t } from '@/locales';

defineOptions({
  name: 'PwdLogin'
});

const authStore = useAuthStore();
// const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useNaiveForm();

interface FormModel {
  userName: string;
  password: string;
  captcha: string;
}

const model: FormModel = reactive({
  userName: 'admin',
  password: 'admin123',
  captcha: ''
});

const captchaInfo = reactive({ key: '', svg: '' });

async function refreshCaptcha() {
  const { data, error } = await fetchCaptcha();
  if (!error && data) {
    captchaInfo.key = data.key;
    captchaInfo.svg = data.svg;
    model.captcha = '';
  }
}

onMounted(() => {
  refreshCaptcha();
});

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  // inside computed to make locale reactive, if not apply i18n, you can define it without computed
  const { formRules } = useFormRules();

  return {
    userName: formRules.userName,
    password: formRules.pwd,
    captcha: [{ required: true, message: $t('page.login.common.codePlaceholder') }]
  };
});

async function handleSubmit() {
  await validate();
  const pass = await authStore.login(model.userName, model.password, {
    key: captchaInfo.key,
    code: model.captcha
  });
  // 登录失败（验证码错误等）后刷新验证码
  if (!pass) {
    refreshCaptcha();
  }
}

// 注释掉：其他账号登录
// type AccountKey = 'super' | 'admin' | 'user';
//
// interface Account {
//   key: AccountKey;
//   label: string;
//   userName: string;
//   password: string;
// }
//
// const accounts = computed<Account[]>(() => [
//   {
//     key: 'super',
//     label: $t('page.login.pwdLogin.superAdmin'),
//     userName: 'Super',
//     password: '123456'
//   },
//   {
//     key: 'admin',
//     label: $t('page.login.pwdLogin.admin'),
//     userName: 'Admin',
//     password: '123456'
//   },
//   {
//     key: 'user',
//     label: $t('page.login.pwdLogin.user'),
//     userName: 'User',
//     password: '123456'
//   }
// ]);
//
// async function handleAccountLogin(account: Account) {
//   await authStore.login(account.userName, account.password);
// }
</script>

<template>
  <NForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <NFormItem path="userName">
      <NInput v-model:value="model.userName" :placeholder="$t('page.login.common.userNamePlaceholder')" />
    </NFormItem>
    <NFormItem path="password">
      <NInput
        v-model:value="model.password"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')"
      />
    </NFormItem>
    <NFormItem path="captcha">
      <div class="w-full flex-y-center gap-12px">
        <NInput
          v-model:value="model.captcha"
          :maxlength="2"
          :placeholder="$t('page.login.common.captchaPlaceholder')"
          class="flex-1"
        />
        <!-- 点击图片刷新验证码 -->
        <div
          class="captcha-img flex-shrink-0 cursor-pointer"
          :title="$t('page.login.common.captchaPlaceholder')"
          @click="refreshCaptcha"
          v-html="captchaInfo.svg"
        ></div>
      </div>
    </NFormItem>
    <NSpace vertical :size="24">
      <NCheckbox>{{ $t('page.login.pwdLogin.rememberMe') }}</NCheckbox>
      <NButton type="primary" size="large" round block :loading="authStore.loginLoading" @click="handleSubmit">
        {{ $t('common.confirm') }}
      </NButton>
      <!-- 注释掉：忘记密码、验证码登录、注册账号、其他账号登录 -->
      <!-- <div class="flex-y-center justify-between">
        <NCheckbox>{{ $t('page.login.pwdLogin.rememberMe') }}</NCheckbox>
        <NButton quaternary @click="toggleLoginModule('reset-pwd')">
          {{ $t('page.login.pwdLogin.forgetPassword') }}
        </NButton>
      </div>
      <div class="flex-y-center justify-between gap-12px">
        <NButton class="flex-1" block @click="toggleLoginModule('code-login')">
          {{ $t(loginModuleRecord['code-login']) }}
        </NButton>
        <NButton class="flex-1" block @click="toggleLoginModule('register')">
          {{ $t(loginModuleRecord.register) }}
        </NButton>
      </div>
      <NDivider class="text-14px text-#666 !m-0">{{ $t('page.login.pwdLogin.otherAccountLogin') }}</NDivider>
      <div class="flex-center gap-12px">
        <NButton v-for="item in accounts" :key="item.key" type="primary" @click="handleAccountLogin(item)">
          {{ item.label }}
        </NButton>
      </div> -->
    </NSpace>
  </NForm>
</template>

<style scoped>
.captcha-img {
  border-radius: 6px;
  overflow: hidden;
  line-height: 0;
  transition: opacity 0.2s;
}

.captcha-img:hover {
  opacity: 0.8;
}
</style>
