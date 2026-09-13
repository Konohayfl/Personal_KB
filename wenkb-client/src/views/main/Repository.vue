<template>
  <LibraryPage class="kb-repos" title="我的知识库" subtitle="整理资料，让知识随时可用。" noun="知识库" create-label="新建知识库" empty-description="把文档和网页归入一个主题，导入资料后即可开始搜索和问答。" :items="sourceRepositoryList" id-key="reposId" title-key="reposNm" desc-key="reposDesc" icon="folder" :loading="loading" :error="loadError" @create="addForm" @open="turnToDetail" @option="onOptionSelect" @retry="initData" />
</template>

<script>
  import { defineComponent, ref, getCurrentInstance } from 'vue'
  import { useRouter } from 'vue-router'
  import { useDialog } from 'naive-ui'

  import { renderIconfontIcon, dialogCreate, dialogConfirm } from '@/libs/utils'
  import { isEmpty, localSave } from '@/libs/tools'
  import { CURRENT_REPOS_ID_KEY } from '@/libs/enum'
  import LibraryPage from '@/views/main/components/LibraryPage.vue'
  import RepositoryForm from './repository/form/RepositoryForm.vue'

  export default defineComponent({
    components: {
      LibraryPage
    },
    setup() {
      const dialog = useDialog()
      // 获取当前组件的实例、上下文来操作router和vuex等。相当于this
	    const { proxy, ctx } = getCurrentInstance()
      const router = useRouter()
      const sourceRepositoryList = ref([])
      const loading = ref(false)
      const loadError = ref(false)
      const initData = () => {
        loading.value = true
        loadError.value = false
        proxy.$api.post('/knb/repository/my/list').then(res => {
          sourceRepositoryList.value = res.data || []
        }).catch(err => {
          loadError.value = true
          console.error(err)
        }).finally(() => { loading.value = false })
      }
      initData()
      const addForm = () => {
        dialogCreate(dialog, {
          title: `新增知识库`,
          style: 'width: min(640px, calc(100vw - 32px));',
          maskClosable: false,
          icon: () => renderIconfontIcon('iconfont-kb icon-knowledge', { size: '28px' }),
          onPositiveClick: (data, e, dialog) => {
            proxy.$api.post('/knb/repository', data).then(res => {
              initData()
            }).catch(err => {
              console.error(err)
            })
            dialog.destroy()
          }
        }, RepositoryForm, {
        })
      }
      const onOptionSelect = (key, repos) => {
        if (key === 'edit') {
          dialogCreate(dialog, {
            title: `修改知识库`,
            style: 'width: min(640px, calc(100vw - 32px));',
            maskClosable: false,
            icon: () => renderIconfontIcon('iconfont-kb icon-knowledge', { size: '28px' }),
            onPositiveClick: (data, e, dialog) => {
              proxy.$api.put('/knb/repository', data).then(res => {
                initData()
                dialog.destroy()
              }).catch(err => {
                console.error(err)
                dialog.destroy()
              })
            }
          }, RepositoryForm, {
            repository: repos
          })
        } else if (key === 'delete') {
          dialogConfirm(dialog, {
            title: '删除',
            content: '确定删除该知识库么？',
            type: 'warning',
            onPositiveClick: (e, dialog) => {
              dialog.loading = true
              proxy.$api.delete('/knb/repository/' + repos.reposId).then(res => {
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
      const turnToDetail = (reposId) => {
        localSave(CURRENT_REPOS_ID_KEY, reposId)
        router.push(`/main/repository/detail?id=${reposId}`)
      }
      return {
        sourceRepositoryList, loading, loadError, initData,
        addForm, onOptionSelect,
        turnToDetail
      }
    }
  })
</script>
