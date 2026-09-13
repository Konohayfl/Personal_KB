<template>
  <div class="kb-card-list" :class="{ 'is-list': view === 'list' }">
    <article v-for="item in dataList" :key="item[idKey]" class="library-card" :class="`tone-${libraryTone(item[idKey])}`">
      <button class="library-card-open" @click="$emit('on-item-click', item[idKey])" :aria-label="`${entryLabel}：${item[titleKey]}`">
        <span class="library-card-icon"><WorkspaceIcon :name="icon" /></span>
        <span class="library-card-body"><strong class="library-card-title" :title="item[titleKey]">{{ item[titleKey] }}</strong><span class="library-card-description">{{ item[descKey] || defaultDesc }}</span></span>
        <span class="library-card-meta"><WorkspaceIcon name="document" />{{ createdLabel(item.crtTm) }}</span>
        <span class="library-card-entry">{{ entryLabel }}<WorkspaceIcon name="arrow" /></span>
      </button>
      <n-dropdown v-if="item.optAuth === 'alter'" trigger="click" :options="options" @select="key => $emit('on-option-select', key, item)">
        <button class="library-card-more" :aria-label="`管理${item[titleKey]}`" title="编辑或删除"><WorkspaceIcon name="more" /></button>
      </n-dropdown>
    </article>
  </div>
</template>

<script setup>
import WorkspaceIcon from '@/components/WorkspaceIcon.vue'
import { createdLabel, libraryTone } from '@/libs/library-view.js'
defineProps({
  dataList: { type: Array, default: () => [] },
  idKey: { type: String, default: 'id' }, titleKey: { type: String, default: 'title' }, descKey: { type: String, default: 'desc' },
  defaultDesc: { type: String, default: '还没有介绍' }, view: { type: String, default: 'grid' },
  entryLabel: { type: String, default: '进入知识库' }, icon: { type: String, default: 'folder' }
})
defineEmits(['on-item-click', 'on-option-select'])
const options = [{ label: '编辑', key: 'edit' }, { label: '删除', key: 'delete' }]
</script>

<style lang="less">
.kb-card-list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; }
.library-card { position: relative; min-width: 0; border: 1px solid var(--workspace-border); border-radius: 10px; background: var(--workspace-panel); transition: border-color .18s, box-shadow .18s; --folder-color: #7fa58a; }
.library-card:hover, .library-card:focus-within { border-color: #a8c3b2; box-shadow: 0 5px 20px #173e2907; }
.library-card.tone-1 { --folder-color: #d39536; }
.library-card.tone-2 { --folder-color: #648cb8; }
.library-card.tone-3 { --folder-color: #9b87c2; }
.library-card.tone-4 { --folder-color: #ce916e; }
.library-card.tone-5 { --folder-color: #67a6a0; }
.library-card-open { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: stretch; padding: 24px; border: 0; border-radius: 10px; background: transparent; text-align: left; color: var(--workspace-text); cursor: pointer; }
.library-card-icon { margin-bottom: 20px; color: var(--folder-color); }
.library-card-icon .workspace-icon { width: 37px; height: 37px; fill: color-mix(in srgb, var(--folder-color) 10%, transparent); }
.library-card-title { display: block; font-size: 18px; font-weight: 600; line-height: 1.5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.library-card-body { display: block; min-width: 0; }
.library-card-description { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; overflow-wrap: anywhere; color: var(--workspace-muted); font-size: 13px; line-height: 1.8; height: 47px; margin-top: 5px; }
.library-card-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 7px; color: var(--workspace-muted); border-top: 1px solid var(--workspace-border); padding-top: 15px; margin-top: 17px; font-size: 12px; }
.library-card-meta .workspace-icon { width: 15px; height: 15px; }
.library-card-entry { display: flex; gap: 12px; align-items: center; color: var(--workspace-accent); margin-top: 18px; font-size: 13px; font-weight: 550; }
.library-card-entry .workspace-icon { width: 17px; height: 17px; }
.library-card-more { position: absolute; top: 18px; right: 16px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border: 0; border-radius: 6px; background: transparent; color: var(--workspace-muted); cursor: pointer; }
.library-card-more:hover { color: var(--workspace-accent); background: var(--workspace-soft); }
.kb-card-list.is-list { grid-template-columns: 1fr; gap: 12px; }
.is-list .library-card-open { display: grid; grid-template-columns: 40px minmax(0, 1fr) auto; column-gap: 20px; align-items: center; padding: 20px 62px 20px 24px; }
.is-list .library-card-icon { margin: 0; grid-row: span 2; }
.is-list .library-card-body { grid-row: span 2; }
.is-list .library-card-description { height: auto; -webkit-line-clamp: 1; }
.is-list .library-card-meta { padding: 0; border: 0; margin: 0; }
.is-list .library-card-entry { margin-top: 6px; font-size: 12px; }
.is-list .library-card-more { top: 50%; transform: translateY(-50%); }
@media (max-width: 1190px) { .kb-card-list { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .kb-card-list { grid-template-columns: 1fr; gap: 16px; }
  .library-card-open { padding: 22px; }
  .is-list .library-card-open { grid-template-columns: 28px minmax(0, 1fr); gap: 10px; padding: 18px 45px 18px 18px; }
  .is-list .library-card-icon .workspace-icon { width: 26px; height: 26px; }
  .is-list .library-card-meta, .is-list .library-card-entry { grid-column: 2; }
  .is-list .library-card-more { right: 8px; }
}
@media (prefers-reduced-motion: reduce) { .library-card { transition: none; } }
</style>
