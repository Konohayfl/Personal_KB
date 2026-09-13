<style lang="less">
.kb-setting {
  height: 100%;
  .n-menu {
    .n-menu-item-content::before {
      left: 0;
      right: 0;
    }
    .n-menu-item-content__icon {
      .n-icon {
        font-size: 20px;
      }
    }
  }
}
</style>

<template>
  <n-layout class="kb-setting" has-sider>
    <n-layout-sider bordered :width="190" content-style="padding: 24px 16px;">
      <n-menu
        v-model:value="activeKey"
        :options="menuOptions"
        responsive
        :on-update:value="onMenuUpdate"
      />
    </n-layout-sider>
    <n-layout-content content-style="padding: 24px;">
      <header class="workspace-section-title"><h1>{{ activeKey === 'theme' ? '外观设置' : '模型设置' }}</h1><p>{{ activeKey === 'theme' ? '让工作空间更适合你的使用习惯。' : '连接模型服务，为知识检索和对话做好准备。' }}</p></header>
      <theme v-if="activeKey==='theme'" />
      <team v-if="activeKey==='team'" />
      <user v-if="activeKey === 'userinfo'" />
      <llm v-if="activeKey === 'llm'" />
    </n-layout-content>
  </n-layout>
</template>
<script>
  import { defineComponent, ref, watch } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { } from 'naive-ui'
  import { renderIconfontIcon } from '@/libs/utils'
  import Theme from './setting/Theme.vue'
  import Team from './setting/Team.vue'
  import User from './setting/User.vue'
  import Llm from './setting/Llm.vue'
  const menuOptions = [
    {
      label: '模型设置',
      key: 'llm',
      icon: () => renderIconfontIcon('iconfont-kb icon-llm')
    },
    {
      label: '外观设置',
      key: 'theme',
      icon: () => renderIconfontIcon('iconfont-kb icon-theme')
    }
  ]
  export default defineComponent({
    components: {
      Theme, Team, User, Llm
    },
    data() {
      return {
      }
    },
    setup() {
      const router = useRouter()
      const route = useRoute()
      const activeKey = ref(router.currentRoute.value.query.menu || 'llm')
      const onMenuUpdate = (key) => {
        router.push(`/main/setting?menu=${key}`)
      }
      watch(() => route.query, (newRouter) => {
        activeKey.value = newRouter.menu || 'llm'
      })
      return {
        router,
        activeKey, menuOptions,
        onMenuUpdate
      }
    }
  })
</script>
