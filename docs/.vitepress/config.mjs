import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "TubeSentry",
  description: "Agentic-First YouTube & Performance Max Placement Waste Auditor & MCP Server",
  base: "/tubesentry/",
  head: [
    ['link', { rel: 'icon', href: '/tubesentry/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#0284c7' }]
  ],
  themeConfig: {
    logo: '🛡️',
    siteTitle: 'TubeSentry',
    nav: [
      { text: 'Guide', link: '/guide/quickstart' },
      { text: 'Creative Profiler', link: '/guide/creative-profiler' },
      { text: 'MCP Server', link: '/guide/mcp-server' },
      { text: 'CLI Reference', link: '/guide/cli' },
      { text: 'TubeSentry Pro', link: '/guide/pro' },
      { text: 'GitHub', link: 'https://github.com/flovv/tubesentry' }
    ],
    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/guide/quickstart' },
          { text: 'Waste Categories', link: '/guide/waste-categories' }
        ]
      },
      {
        text: 'Core Features',
        items: [
          { text: 'Creative Targeting Fit (Gemini)', link: '/guide/creative-profiler' },
          { text: 'Claude & Cursor MCP Server', link: '/guide/mcp-server' },
          { text: 'CLI Reference', link: '/guide/cli' },
          { text: 'Python SDK', link: '/guide/python-sdk' }
        ]
      },
      {
        text: 'Commercial Edition',
        items: [
          { text: 'TubeSentry Pro & 65k Shield', link: '/guide/pro' }
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/flovv/tubesentry' }
    ],
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026 TubeSentry Core Contributors'
    },
    search: {
      provider: 'local'
    }
  }
})
