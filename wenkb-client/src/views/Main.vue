<style lang="less">
@import url('./workspace.less');
</style>

<template>
  <div class="kb-main" :class="`kb-navi-${naviType}`">
    <a class="workspace-skip" href="#workspace-content" @click.prevent="$refs.content.focus()">跳到内容</a>
    <aside class="workspace-sidebar" aria-label="工作空间侧栏">
      <router-link to="/main/repository" class="workspace-brand" aria-label="WenKB 知识库首页">
        <WorkspaceIcon name="book" />
        <span><strong>WenKB</strong><small>个人知识空间</small></span>
      </router-link>
      <nav class="workspace-nav" aria-label="主导航">
        <router-link v-for="item in workspaceNav" :key="item.key" :to="`/main/${item.key}`" :class="{ active: activeKey === item.key }" :aria-current="activeKey === item.key ? 'page' : undefined" :title="item.label" :aria-label="item.label">
          <WorkspaceIcon :name="item.icon" /><span>{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="workspace-sidebar-bottom">
        <router-link to="/main/setting" class="workspace-settings" :class="{ active: activeKey === 'setting' }" :aria-current="activeKey === 'setting' ? 'page' : undefined" title="设置" aria-label="设置">
          <WorkspaceIcon name="settings" /><span>设置</span>
        </router-link>
        <div class="workspace-local"><WorkspaceIcon name="drive" /><span>本地工作区</span>
          <button class="workspace-theme" @click="onThemeTypeChange" :aria-label="`切换${themeType === 'dark' ? '浅' : '深'}色主题`" :title="`切换${themeType === 'dark' ? '浅' : '深'}色主题`"><WorkspaceIcon :name="themeType === 'dark' ? 'moon' : 'sun'" /></button>
        </div>
      </div>
    </aside>
    <div class="workspace-main">
      <header class="workspace-topbar">
        <div class="workspace-breadcrumb"><router-link to="/main/repository">工作空间</router-link><span>/</span><span>{{ currentPageLabel }}</span><template v-if="isDetail"><span>/</span><span>详情</span></template></div>
        <div class="workspace-connection" :class="connection" role="status"><i></i>{{ connectionLabel }}</div>
      </header>
      <main ref="content" id="workspace-content" class="workspace-content" tabindex="-1"><router-view /></main>
    </div>
  </div>
</template>
<script>
  import { defineComponent, onBeforeUnmount, onMounted, computed, getCurrentInstance, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { localRead, localSave } from '@/libs/tools'
  import { THEME_TYPE_KEY, DEFAULT_THEME_TYPE } from '@/libs/enum'
  import { useTheme } from '@/mixin/app'
  import EventBus from '@/libs/eventbus'
  import WorkspaceIcon from '@/components/WorkspaceIcon.vue'

  export default defineComponent({
    components: {
      WorkspaceIcon
    },
    setup() {
      const router = useRouter()
      const { proxy } = getCurrentInstance()
      const workspaceNav = [
        { key: 'repository', label: '知识库', icon: 'folder' },
        { key: 'chat', label: '对话', icon: 'chat' },
        { key: 'search', label: '搜索', icon: 'search' },
        { key: 'docset', label: '文档库', icon: 'document' }
      ]
      const currentPageLabel = computed(() => [...workspaceNav, { key: 'setting', label: '设置' }, { key: 'appinfo', label: '应用' }].find(item => router.currentRoute.value.path.split('/').includes(item.key))?.label || '工作空间')
      const isDetail = computed(() => router.currentRoute.value.path.endsWith('/detail'))
      const connection = ref('checking')
      const connectionLabel = computed(() => ({ checking: '连接中', online: '本地服务已连接', offline: '本地服务未连接' }[connection.value]))
      const checkConnection = async () => {
        try {
          const result = await proxy.$api.get('/health', {}, { timeout: 5000 })
          connection.value = result.success && result.data?.status === 'ok' ? 'online' : 'offline'
        } catch { connection.value = 'offline' }
      }
      let healthTimer
      onMounted(() => { checkConnection(); healthTimer = setInterval(checkConnection, 60000) })
      onBeforeUnmount(() => clearInterval(healthTimer))
      const { naviType } = useTheme()
      const getKeyByPath = (path) => {
        const currentPaths = path.split('/')
        return currentPaths.find(item => [...workspaceNav.map(menu => menu.key), 'setting', 'appinfo'].includes(item))
      }
      const activeKey = ref(getKeyByPath(router.currentRoute.value.path))
      const themeType = ref(localRead(THEME_TYPE_KEY) || DEFAULT_THEME_TYPE) // light, dark
      const onThemeTypeChange = (type) => {
        if (typeof type === 'string') {
          themeType.value = type
          return
        }
        if (themeType.value === 'dark') {
          themeType.value = 'light'
        } else {
          themeType.value = 'dark'
        }
      }
      watch(themeType, (newTheme, oldTheme)=>{
        localSave(THEME_TYPE_KEY, newTheme)
        EventBus.emit('on-theme-type-change', newTheme)
      })

      watch(() => router.currentRoute.value, (newRouter) => {
        let key = getKeyByPath(newRouter.path)
        activeKey.value = key
      }, { immediate: true })

      const synth = window.speechSynthesis
      const speech = new SpeechSynthesisUtterance()
      speech.lang = 'zh-CN' // 使用的语言:中文
      speech.volume = 1 // 声音音量：1
      speech.rate = 1 // 语速：1
      speech.pitch = 1 // 音高：1
      speech.onend = () => {
        EventBus.emit('on-speech-onend')
      }

      const onSpeechOn = (text) => {
        onSpeechOff()
        speech.text = text // 文字内容: 如果能播放出声音 那可真是泰裤辣！
        synth.speak(speech) // 播放
      }
      const onSpeechOff = () => {
        EventBus.emit('on-speech-onend')
        speech.text = ''
        synth.cancel(speech)
      }

      EventBus.on('on-speech-on', onSpeechOn)
      EventBus.on('on-speech-off', onSpeechOff)
      EventBus.on('on-theme-type-change', onThemeTypeChange)
      onBeforeUnmount(() => {
        EventBus.off('on-speech-on', onSpeechOn)
        EventBus.off('on-speech-off', onSpeechOff)
        EventBus.off('on-theme-type-change', onThemeTypeChange)
      })
      return {
        workspaceNav, currentPageLabel, isDetail, connection, connectionLabel,
        themeType, naviType,
        activeKey,
        onThemeTypeChange
      }
    }
  })
</script>
