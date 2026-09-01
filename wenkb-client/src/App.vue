<style lang="less">
@import url('./window.less');
.n-config-provider, .kb-app {
  height: 100%;
}
</style>

<template>
  <n-config-provider :theme="themeType" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-el tag="div" id="kb-app" :class="`kb-app ${themeType.name}`">
      <n-dialog-provider>
        <n-message-provider>
          <router-view />
          <m-n-d />
        </n-message-provider>
      </n-dialog-provider>
    </n-el>
  </n-config-provider>
</template>
<script>
  import { defineComponent } from 'vue'
  import { useTheme } from '@/mixin/app'
  import MND from './components/MND.vue'
  
  export default defineComponent({
    components: {
      MND
    },
    setup() {
      const {themeOverrides, themeType, zhCN, dateZhCN} = useTheme()
      return {
        themeOverrides, themeType, zhCN, dateZhCN
      }
    }
  })
</script>
