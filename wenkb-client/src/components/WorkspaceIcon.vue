<template>
  <svg class="workspace-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path v-for="(path, index) in (paths[name] || paths.book)" :key="index" :d="path" />
  </svg>
</template>

<script setup>
defineProps({ name: { type: String, default: 'book' } })
const paths = {
  book: ['M12 5.5C9 3.5 5.5 3 2.5 4v15c3-1 6.5-.5 9.5 1.5 3-2 6.5-2.5 9.5-1.5V4c-3-1-6.5-.5-9.5 1.5Z', 'M12 5.5v15'],
  folder: ['M3 6a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z'],
  chat: ['M21 11.5a8.5 8.5 0 0 1-8.5 8.5H4l-2 2V11.5a9.5 9.5 0 0 1 19 0Z', 'M7 9h9M7 13h6'],
  search: ['M16.5 16.5 21 21', 'M18 10.5a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z'],
  document: ['M14 2H5a1 1 0 0 0-1 1v18a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V8Z', 'M14 2v6h6M8 12h8M8 16h6'],
  settings: ['M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z', 'm10 2-.6 2.3-2 .9-2.2-.6-2 3.4 1.6 1.7-.2 2.3L3 13.8l2 3.4 2.3-.5 1.9 1L10 20h4l.7-2.3 2-1 2.3.5 2-3.4-1.6-1.8-.2-2.3L21 8l-2-3.4-2.2.6-2-.9L14 2Z'],
  grid: ['M3 3h7v7H3ZM14 3h7v7h-7ZM3 14h7v7H3ZM14 14h7v7h-7Z'],
  list: ['M8 5h13M8 12h13M8 19h13M3 5h.01M3 12h.01M3 19h.01'],
  plus: ['M12 5v14M5 12h14'],
  arrow: ['M4 12h16m-6-6 6 6-6 6'],
  chevron: ['m9 5 7 7-7 7'],
  more: ['M5 12h.01M12 12h.01M19 12h.01'],
  drive: ['M5 3h14l3 14v4H2v-4ZM2 17h20M17 19h1'],
  sun: ['M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.4 1.4M17.6 17.6 19 19M5 19l1.4-1.4M17.6 6.4 19 5'],
  moon: ['M21 13a9 9 0 0 1-10-10A9.2 9.2 0 1 0 21 13Z'],
  close: ['m6 6 12 12M6 18 18 6'],
}
</script>

<style>
.workspace-icon { display: inline-block; width: 22px; height: 22px; flex-shrink: 0; vertical-align: middle; }
</style>
