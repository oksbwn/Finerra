import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { h } from 'vue'
import * as lucideIcons from 'lucide-vue-next'

/**
 * Custom Lucide Icon Set for Vuetify 3
 */
const lucide: any = {
    component: (props: any) => {
        const iconName = props.icon
        const icon = (lucideIcons as any)[iconName]
        return icon ? h(icon, { ...props }) : null
    }
}

export default createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'lucide',
        sets: {
            lucide,
        },
    },
    theme: {
        defaultTheme: 'wealthFamTheme',
        themes: {
            wealthFamTheme: {
                dark: false,
                colors: {
                    primary: '#4f46e5',
                    secondary: '#8b5cf6',
                    accent: '#0ea5e9',
                    error: '#ef4444',
                    info: '#3b82f6',
                    success: '#10b981',
                    warning: '#f59e0b',
                    background: '#f8fafc',
                    surface: '#ffffff',
                },
            },
        },
    },
})
