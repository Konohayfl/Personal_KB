// Dev-only fixture: no API client, no database writes, not a production entry point.
import { createApp } from 'vue'
import Fixture from './ui-fixture.vue'
import '../src/style.less'
import '../src/views/workspace.less'
createApp(Fixture).mount('#app')
