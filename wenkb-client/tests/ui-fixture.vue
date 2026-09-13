<template>
  <n-config-provider :theme="themeType" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-el class="kb-app light">
      <div style="padding:12px;display:flex;gap:12px;flex-wrap:wrap">
        <button @click="state = 'loaded'">六张示例卡片</button><button @click="state = 'empty'">空数据</button><button @click="state = 'error'">加载失败</button><button @click="state = 'loading'">加载中</button>
        <output aria-label="最后事件">{{ event }}</output>
      </div>
      <LibraryPage title="我的知识库" subtitle="独立测试页面，所有资料均为测试数据。" noun="知识库" create-label="新建知识库" empty-description="建立知识库后即可导入文档。" :items="state === 'empty' ? [] : items" id-key="reposId" title-key="reposNm" desc-key="reposDesc" :loading="state === 'loading'" :error="state === 'error'" @create="event = 'create'" @open="id => event = `open:${id}`" @option="(key, item) => event = `${key}:${item.reposId}`" @retry="state = 'loaded'; event = 'retry'" />
    </n-el>
  </n-config-provider>
</template>
<script setup>
import { ref } from 'vue'
import { useTheme } from '../src/mixin/app'
import LibraryPage from '../src/views/main/components/LibraryPage.vue'
const { themeType, themeOverrides, zhCN, dateZhCN } = useTheme()
const state = ref('loaded')
const event = ref('none')
const items = [
  ['产品设计', '设计规范、用户研究与产品灵感'], ['技术笔记', '开发实践、架构设计与问题记录'],
  ['阅读与思考', '读书笔记、摘录与长期积累'], ['项目资料', '需求文档、会议记录与交付资料'],
  ['学习计划', '课程资料与阶段性学习笔记'], ['很长的知识库名称用于检查省略显示及列表布局是否正确', '']
].map(([reposNm, reposDesc], index) => ({ reposId: `fixture-${index}`, reposNm, reposDesc, crtTm: `2026-09-0${index + 1} 12:00:00`, optAuth: index === 5 ? 'visit' : 'alter' }))
</script>
