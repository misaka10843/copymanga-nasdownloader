// frontend/src/plugins/vuetify.js
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { md3 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as labsComponents from 'vuetify/labs/components'

export default createVuetify({
  blueprint: md3,
    components: {
    ...components,
    ...labsComponents,
  },
  theme: {
    defaultTheme: 'myCustomTheme',
    themes: {
      myCustomTheme: {
        dark: false,
        colors: {
          primary: '#6750A4', // M3 标准紫
          secondary: '#625B71',
          surface: '#FEF7FF',
          'surface-variant': '#E7E0EC',
          background: '#FDFBFF',
          error: '#B3261E',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
    },
  },
  defaults: {
    VCard: {
      elevation: 2,
      rounded: 'xl',
    },
    VBtn: {
      rounded: 'pill',
      variant: 'flat',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
  },
})