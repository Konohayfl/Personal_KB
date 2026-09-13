<template>
  <section class="library-page" :aria-label="title">
    <header class="library-heading">
      <div><h1>{{ title }}</h1><p>{{ subtitle }}</p></div>
      <n-button type="primary" size="large" @click="$emit('create')"><template #icon><WorkspaceIcon name="plus" /></template>{{ createLabel }}</n-button>
    </header>
    <div class="library-toolbar">
      <n-input v-model:value="query" clearable :placeholder="`搜索${noun}…`" :input-props="{ 'aria-label': `搜索${noun}` }">
        <template #prefix><WorkspaceIcon name="search" /></template>
      </n-input>
      <n-select v-model:value="sort" :options="sortOptions" aria-label="排序方式" class="library-sort" />
      <div class="library-view-toggle" role="group" aria-label="显示方式">
        <button :class="{ active: view === 'grid' }" :aria-pressed="view === 'grid'" aria-label="网格视图" title="网格视图" @click="view = 'grid'"><WorkspaceIcon name="grid" /></button>
        <button :class="{ active: view === 'list' }" :aria-pressed="view === 'list'" aria-label="列表视图" title="列表视图" @click="view = 'list'"><WorkspaceIcon name="list" /></button>
      </div>
    </div>
    <div class="library-summary" aria-live="polite"><span>{{ query.trim() ? '搜索结果' : `全部${noun}` }}</span><span class="library-count">{{ visibleItems.length }}</span></div>
    <div v-if="loading" class="library-skeletons" role="status" aria-label="加载中"><n-skeleton v-for="n in 3" :key="n" height="225px" :sharp="false" /></div>
    <div v-else-if="error" class="library-empty" role="alert">
      <WorkspaceIcon name="drive" /><h2>暂时无法加载{{ noun }}</h2><p>请确认本地服务已启动，然后重试。</p><n-button @click="$emit('retry')">重新加载</n-button>
    </div>
    <CardList v-else-if="visibleItems.length" :data-list="visibleItems" :id-key="idKey" :title-key="titleKey" :desc-key="descKey" :default-desc="`这个${noun}还没有介绍`" :view="view" :entry-label="`进入${noun}`" :icon="icon" @on-item-click="id => $emit('open', id)" @on-option-select="(key, item) => $emit('option', key, item)" />
    <div v-else class="library-empty">
      <WorkspaceIcon :name="query.trim() ? 'search' : icon" />
      <h2>{{ query.trim() ? '没有找到匹配的内容' : `建立你的第一个${noun}` }}</h2>
      <p>{{ query.trim() ? '试试其他关键词，或清除搜索查看全部内容。' : emptyDescription }}</p>
      <n-button v-if="query.trim()" @click="query = ''">清除搜索</n-button>
      <n-button v-else type="primary" @click="$emit('create')"><template #icon><WorkspaceIcon name="plus" /></template>{{ createLabel }}</n-button>
    </div>
    <footer class="library-guide">
      <WorkspaceIcon name="book" /><span>从第一份资料开始，建立你的知识网络。</span>
      <button @click="guideOpen = true">查看使用指南<WorkspaceIcon name="arrow" /></button>
    </footer>
    <n-modal v-model:show="guideOpen" preset="card" title="开始使用 WenKB" class="library-guide-modal" style="width: min(560px, calc(100vw - 32px))">
      <ol class="library-guide-steps">
        <li><strong>建立知识库</strong><p>按项目或主题整理资料，选择索引模型。</p></li>
        <li><strong>导入并启用资料</strong><p>在知识库详情中上传文档或添加网页链接，等待索引就绪。</p></li>
        <li><strong>配置模型，开始提问</strong><p>在设置中配置模型供应商并选择默认聊天模型，再到对话页提问和查看引用。</p></li>
      </ol>
      <template #footer><n-button type="primary" @click="guideOpen = false">知道了</n-button></template>
    </n-modal>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import WorkspaceIcon from '@/components/WorkspaceIcon.vue'
import CardList from './CardList.vue'
import { selectLibraries } from '@/libs/library-view.js'

const props = defineProps({
  title: String, subtitle: String, noun: String, createLabel: String, emptyDescription: String,
  items: { type: Array, default: () => [] },
  idKey: String, titleKey: String, descKey: String,
  icon: { type: String, default: 'folder' }, loading: Boolean, error: Boolean
})
defineEmits(['create', 'retry', 'open', 'option'])
const query = ref('')
const sort = ref('newest')
const view = ref('grid')
const guideOpen = ref(false)
const sortOptions = [{ label: '最近创建', value: 'newest' }, { label: '最早创建', value: 'oldest' }, { label: '名称排序', value: 'name' }]
const visibleItems = computed(() => selectLibraries(props.items, query.value, sort.value, props.titleKey))
</script>

<style lang="less">
.library-page { padding: 32px 40px; max-width: 1680px; margin: 0 auto; min-height: 100%; display: flex; flex-direction: column; }
.library-heading { display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-bottom: 30px; }
.library-heading h1 { font-size: 30px; line-height: 1.4; font-weight: 700; letter-spacing: -.8px; margin-bottom: 7px; }
.library-heading p { color: var(--workspace-muted); font-size: 14px; }
.library-heading > .n-button { flex-shrink: 0; padding: 0 22px; }
.library-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; }
.library-toolbar > .n-input { flex: 1; }
.library-toolbar .workspace-icon { width: 19px; height: 19px; color: var(--workspace-muted); }
.library-sort { width: 150px; flex-shrink: 0; }
.library-view-toggle { display: flex; padding: 3px; border: 1px solid var(--workspace-border); background: var(--workspace-panel); border-radius: 8px; }
.library-view-toggle button { display: flex; align-items: center; justify-content: center; background: transparent; border: none; cursor: pointer; width: 40px; height: 32px; border-radius: 5px; }
.library-view-toggle button.active { background: var(--workspace-soft); }
.library-view-toggle button.active .workspace-icon { color: var(--workspace-accent); }
.library-summary { display: flex; gap: 12px; align-items: center; font-size: 14px; margin-bottom: 18px; }
.library-count { font-size: 12px; border-radius: 5px; background: var(--workspace-soft); padding: 0 7px; color: var(--workspace-muted); }
.library-skeletons { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; }
.library-empty { flex: 1; display: flex; min-height: 350px; flex-direction: column; align-items: center; justify-content: center; text-align: center; border: 1px dashed var(--workspace-border); border-radius: 12px; background: var(--workspace-panel); padding: 40px 20px; gap: 16px; }
.library-empty > .workspace-icon { width: 50px; height: 50px; color: #85a991; margin-bottom: 6px; }
.library-empty h2 { font-weight: 600; font-size: 21px; }
.library-empty p { color: var(--workspace-muted); max-width: 430px; line-height: 1.8; }
.library-guide { margin-top: 24px; padding: 20px 24px; background: var(--workspace-soft); border: 1px solid var(--workspace-border); border-radius: 8px; display: flex; align-items: center; gap: 20px; font-size: 13px; }
.library-guide > .workspace-icon { width: 28px; height: 28px; color: var(--workspace-accent); }
.library-guide button { display: flex; align-items: center; gap: 10px; margin-left: auto; background: none; border: 0; color: var(--workspace-accent); cursor: pointer; white-space: nowrap; font-size: 13px; }
.library-guide button:hover { text-decoration: underline; }
.library-guide button .workspace-icon { width: 18px; }
.library-guide-steps { padding-left: 22px; }
.library-guide-steps li { padding: 10px 0; }
.library-guide-steps p { margin: 6px 0 0; opacity: .75; line-height: 1.8; }
@media (min-width: 1700px) { .library-page { padding-left: 56px; padding-right: 56px; } }
@media (max-width: 1100px) { .library-page { padding: 28px 24px; } .library-heading h1 { font-size: 27px; } }
@media (max-width: 760px) {
  .library-page { padding: 24px 18px; }
  .library-heading { flex-wrap: wrap; margin-bottom: 24px; }
  .library-heading h1 { font-size: 25px; }
  .library-toolbar { flex-wrap: wrap; gap: 10px; }
  .library-toolbar > .n-input { flex-basis: 100%; }
  .library-sort { flex: 1; }
  .library-empty { min-height: 330px; }
  .library-skeletons { grid-template-columns: 1fr; }
  .library-guide { flex-wrap: wrap; padding: 18px; gap: 12px; }
  .library-guide > span { flex: 1; min-width: 140px; }
  .library-guide button { margin-left: 40px; }
}
</style>
