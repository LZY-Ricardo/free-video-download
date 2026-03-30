<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import { useAuth } from '@/composables/useAuth'

const props = withDefaults(defineProps<{
  open: boolean
  mode?: 'login' | 'register'
}>(), {
  mode: 'login',
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'login-success'): void
}>()

const {
  submitting,
  error,
  registerMessage,
  debugVerifyUrl,
  login,
  register,
  clearFeedback,
} = useAuth()

const activeMode = ref<'login' | 'register'>(props.mode)
const loginForm = reactive({
  email: '',
  password: '',
})
const registerForm = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})
const localError = ref<string | null>(null)

watch(
  () => props.mode,
  (nextMode) => {
    activeMode.value = nextMode
    localError.value = null
    clearFeedback()
  },
)

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      loginForm.email = ''
      loginForm.password = ''
      registerForm.email = ''
      registerForm.password = ''
      registerForm.confirmPassword = ''
      localError.value = null
      clearFeedback()
    }
  },
)

const switchMode = (mode: 'login' | 'register') => {
  activeMode.value = mode
  localError.value = null
  clearFeedback()
}

const handleClose = () => {
  emit('close')
}

const handleLogin = async () => {
  localError.value = null
  try {
    await login({
      email: loginForm.email,
      password: loginForm.password,
    })
    emit('login-success')
  } catch {
    // composable 内部已填充错误信息
  }
}

const handleRegister = async () => {
  localError.value = null
  if (registerForm.password !== registerForm.confirmPassword) {
    localError.value = '两次输入的密码不一致'
    return
  }

  try {
    await register({
      email: registerForm.email,
      password: registerForm.password,
    })
  } catch {
    // composable 内部已填充错误信息
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[1300] bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4"
      @click.self="handleClose"
    >
      <div class="w-full max-w-md rounded-2xl bg-white border border-gray-200 shadow-xl overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">账号中心</h3>
            <p class="text-xs text-gray-500 mt-1">登录后可购买会员并解锁 AI 学习助手</p>
          </div>
          <button
            class="text-sm text-gray-400 hover:text-gray-700 transition-colors"
            @click="handleClose"
          >
            关闭
          </button>
        </div>

        <div class="px-5 pt-4">
          <div class="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50">
            <button
              class="px-4 py-2 rounded-md text-sm font-medium transition-colors"
              :class="activeMode === 'login' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500'"
              @click="switchMode('login')"
            >
              登录
            </button>
            <button
              class="px-4 py-2 rounded-md text-sm font-medium transition-colors"
              :class="activeMode === 'register' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500'"
              @click="switchMode('register')"
            >
              注册
            </button>
          </div>
        </div>

        <div class="px-5 py-5">
          <div v-if="localError || error" class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {{ localError || error }}
          </div>

          <div v-if="activeMode === 'login'" class="space-y-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">邮箱</label>
              <input
                v-model="loginForm.email"
                type="email"
                class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">密码</label>
              <input
                v-model="loginForm.password"
                type="password"
                class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="至少 8 位"
                @keyup.enter="handleLogin"
              />
            </div>
            <button
              class="w-full rounded-lg bg-blue-600 text-white py-2.5 text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              :disabled="submitting"
              @click="handleLogin"
            >
              {{ submitting ? '登录中...' : '登录账号' }}
            </button>
          </div>

          <div v-else class="space-y-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">邮箱</label>
              <input
                v-model="registerForm.email"
                type="email"
                class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">密码</label>
              <input
                v-model="registerForm.password"
                type="password"
                class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="至少 8 位"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">确认密码</label>
              <input
                v-model="registerForm.confirmPassword"
                type="password"
                class="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="再次输入密码"
                @keyup.enter="handleRegister"
              />
            </div>
            <button
              class="w-full rounded-lg bg-blue-600 text-white py-2.5 text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              :disabled="submitting"
              @click="handleRegister"
            >
              {{ submitting ? '注册中...' : '注册账号' }}
            </button>

            <div v-if="registerMessage" class="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
              <p>{{ registerMessage }}</p>
              <a
                v-if="debugVerifyUrl"
                class="mt-2 inline-flex text-blue-600 hover:text-blue-700 underline underline-offset-2"
                :href="debugVerifyUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                开发环境：点击这里直接完成邮箱验证
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
