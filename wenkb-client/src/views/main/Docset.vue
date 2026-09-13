<template>
  <LibraryPage class="kb-docset" title="我的文档库" subtitle="记录想法，沉淀每一份有价值的内容。" noun="文档集" create-label="新建文档集" empty-description="将笔记、草稿和项目文档整理到一起，随时编辑并保留版本。" :items="sourceDocsetList" id-key="setId" title-key="setNm" desc-key="setDesc" icon="document" :loading="loading" :error="loadError" @create="addForm" @open="turnToDetail" @option="onOptionSelect" @retry="initData" />
</template>

<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog } from 'naive-ui'

  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { isEmpty } from '@/libs/tools'
  import LibraryPage from '@/views/main/components/LibraryPage.vue'
  import DocsetForm from './docset/form/DocsetForm.vue'

  export default defineComponent({
    components: {
      LibraryPage
    },
    setup() {
      const dialog = useDialog()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const sourceDocsetList = ref([])
      const loading = ref(false)
      const loadError = ref(false)
      const initData = () => {
        loading.value = true
        loadError.value = false
        proxy.$api.post('/doc/docset/my/list').then(res => {
          sourceDocsetList.value = res.data || []
        }).catch(err => {
          loadError.value = true
          console.error(err)
        }).finally(() => { loading.value = false })
      }
      initData()
      const addForm = () => {
        dialogCreate(dialog, {
          title: `新增文档集`,
          style: 'width: min(640px, calc(100vw - 32px));',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-docset', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/doc/docset', data).then(res => {
              initData()
            }).catch(err => {
              console.error(err)
            })
            dialog.destroy()
          }
        }, DocsetForm, {
        })
      }
      const onOptionSelect = (key, docset) => {
        if (key === 'edit') {
          dialogCreate(dialog, {
            title: `修改文档集`,
            style: 'width: min(640px, calc(100vw - 32px));',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-docset', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              proxy.$api.put('/doc/docset', data).then(res => {
                initData()
              }).catch(err => {
                console.error(err)
              })
              dialog.destroy()
            }
          }, DocsetForm, {
            docset
          })
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该文档集么？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/doc/docset/' + docset.setId).then(res => {
                initData()
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
              return false
            }
          })
        }
      }
      const turnToDetail = (setId) => {
        router.push(`/main/docset/detail?id=${setId}`)
      }
      return {
        sourceDocsetList, loading, loadError, initData,
        addForm, onOptionSelect,
        turnToDetail
      }
    }
  })
</script>
