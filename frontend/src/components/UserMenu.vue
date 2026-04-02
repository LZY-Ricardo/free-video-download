<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import type { MembershipStatusResponse, UserProfile } from '@/types'

const props = defineProps<{
  user: UserProfile | null
  membership: MembershipStatusResponse | null
  checkoutLoading: boolean
  paymentOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'start-checkout'): void
  (e: 'logout'): void
}>()

const open = ref(false)
const rootRef = ref<HTMLElement | null>(null)

const isMember = computed(() => !!props.membership?.is_member)
const memberSummary = computed(() => {
  if (!props.membership?.is_member) {
    return '当前为免费版'
  }
  return `VIP 有效期还剩 ${props.membership.remaining_days} 天`
})

const checkoutLabel = computed(() => {
  if (!props.paymentOpen) {
    return '支付敬请期待'
  }
  if (props.checkoutLoading) {
    return '正在跳转...'
  }
  return isMember.value ? '续费 VIP 权益' : '立即开通 VIP'
})

const displayInitial = computed(() => {
  const email = props.user?.email?.trim()
  if (!email) {
    return 'U'
  }
  return email.charAt(0).toUpperCase()
})

const maskedEmail = computed(() => {
  const email = props.user?.email?.trim()
  if (!email) {
    return '未登录'
  }
  const parts = email.split('@')
  const localPart = parts[0]
  const domain = parts[1]
  if (!localPart || !domain) {
    return email
  }
  if (localPart.length <= 2) {
    return `${localPart.charAt(0) || '*'}***@${domain}`
  }
  return `${localPart.slice(0, 2)}***@${domain}`
})

const closeMenu = () => {
  open.value = false
}

const toggleMenu = () => {
  open.value = !open.value
}

const handleStartCheckout = () => {
  emit('start-checkout')
  closeMenu()
}

const handleLogout = () => {
  emit('logout')
  closeMenu()
}

const handleGlobalPointerDown = (event: MouseEvent | TouchEvent) => {
  if (!open.value || !rootRef.value) {
    return
  }
  const target = event.target as Node | null
  if (!target || rootRef.value.contains(target)) {
    return
  }
  closeMenu()
}

const handleGlobalKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleGlobalPointerDown)
  document.addEventListener('touchstart', handleGlobalPointerDown, { passive: true })
  document.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleGlobalPointerDown)
  document.removeEventListener('touchstart', handleGlobalPointerDown)
  document.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <div ref="rootRef" class="relative">
    <button
      class="user-pill inline-flex items-center gap-2 rounded-full px-2.5 py-1.5 transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/45 focus-visible:ring-offset-2 focus-visible:ring-offset-white"
      type="button"
      :aria-expanded="open"
      aria-haspopup="menu"
      aria-label="打开用户中心菜单"
      @click="toggleMenu"
    >
      <span class="avatar-badge relative inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold text-white">
        {{ displayInitial }}
        <span class="status-dot" :class="isMember ? 'status-member' : 'status-guest'" />
      </span>
      <span class="hidden sm:inline text-sm font-medium text-slate-700">用户中心</span>
      <svg
        class="h-4 w-4 text-slate-500 transition-transform duration-200"
        :class="open ? 'rotate-180' : ''"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition name="menu-fade">
      <div
        v-if="open"
        class="menu-card absolute right-0 top-[calc(100%+10px)] z-40 w-[290px] max-w-[calc(100vw-1.5rem)] rounded-2xl p-3"
        role="menu"
      >
        <section class="menu-section p-2">
          <p class="text-xs font-medium tracking-wide text-slate-500">账号信息</p>
          <p class="mt-1 text-sm font-semibold text-slate-800">{{ maskedEmail }}</p>
        </section>

        <section class="menu-section mt-2 p-2">
          <div class="flex items-center justify-between">
            <p class="text-xs font-medium tracking-wide text-slate-500">会员状态</p>
            <span class="vip-badge rounded-full px-2 py-0.5 text-[11px] font-semibold" :class="isMember ? 'vip-badge-active' : 'vip-badge-idle'">
              {{ isMember ? 'VIP' : '普通版' }}
            </span>
          </div>
          <p class="mt-1 text-sm text-slate-700">{{ memberSummary }}</p>
          <p class="mt-1 text-xs text-slate-500">
            {{ isMember ? '已解锁 AI 学习助手全部能力' : '开通后可解锁 AI 学习助手全部能力' }}
          </p>
          <button
            class="menu-cta mt-3 w-full rounded-lg px-3 py-2 text-sm font-medium text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/45 focus-visible:ring-offset-2 focus-visible:ring-offset-white disabled:cursor-not-allowed disabled:bg-slate-300"
            :disabled="checkoutLoading"
            @click="handleStartCheckout"
          >
            {{ checkoutLabel }}
          </button>
        </section>

        <section class="menu-section mt-2 border-t border-slate-200/70 px-2 pt-2">
          <button
            class="logout-btn w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-500 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500/30 focus-visible:ring-offset-2 focus-visible:ring-offset-white"
            role="menuitem"
            @click="handleLogout"
          >
            安全退出
          </button>
        </section>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.user-pill {
  border: 1px solid rgba(59, 130, 246, 0.24);
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.96), rgba(219, 234, 254, 0.88));
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.14);
}

.user-pill:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.2);
}

.avatar-badge {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 65%, #1d4ed8 100%);
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.24);
}

.status-dot {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  border: 2px solid #fff;
}

.status-member {
  background: #22c55e;
  --status-color: 34, 197, 94;
  animation: statusPulse 2s ease-in-out infinite;
}

.status-guest {
  background: #f59e0b;
  --status-color: 245, 158, 11;
  animation: statusPulse 2.4s ease-in-out infinite;
}

.menu-card {
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
  backdrop-filter: blur(16px);
  transform-origin: top right;
}

.menu-section {
  border-radius: 10px;
}

.menu-cta {
  background: linear-gradient(135deg, #2563eb, #1d4ed8 62%, #1e40af);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.25);
}

.menu-cta:hover {
  filter: brightness(1.03);
}

.vip-badge-active {
  color: #1e3a8a;
  background: rgba(191, 219, 254, 0.8);
}

.vip-badge-idle {
  color: #b45309;
  background: rgba(254, 215, 170, 0.72);
}

.logout-btn:hover {
  color: #dc2626;
  background: rgba(248, 113, 113, 0.08);
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

@keyframes statusPulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(var(--status-color), 0.22);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(var(--status-color), 0);
    transform: scale(1.04);
  }
}

@media (prefers-reduced-motion: reduce) {
  .status-member,
  .status-guest {
    animation: none;
  }

  .menu-fade-enter-active,
  .menu-fade-leave-active,
  .user-pill,
  .menu-cta,
  .logout-btn {
    transition: none !important;
  }
}

@media (max-width: 640px) {
  .menu-card {
    right: -0.25rem;
  }
}
</style>
