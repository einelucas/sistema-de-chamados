import { fileURLToPath } from 'node:url'
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },

  // SPA client with a live Nitro server for the authenticated API gateway.
  ssr: false,
  serverDir: fileURLToPath(new URL('./server', import.meta.url)),
  nitro: { preset: process.env.VERCEL ? 'vercel' : 'node-server' },

  modules: ["@pinia/nuxt"],

  srcDir: "app/",

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    apiBase: process.env.NUXT_API_BASE || process.env.NUXT_PUBLIC_API_BASE || '',
    public: {
      apiBase:
        process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1",
    },
  },

  app: {
    head: {
      title: "Nexotiva | Central de Chamados",
      script: [
        {
          innerHTML:
            "(function(){try{var t=localStorage.getItem('central_theme');t=t==='dark'?'dark':'light';document.documentElement.dataset.theme=t;document.documentElement.style.colorScheme=t}catch(e){document.documentElement.dataset.theme='light'}})();",
          tagPosition: "head",
        },
      ],
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          name: "description",
          content: "Central de atendimento Nexotiva",
        },
      ],
    },
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },
});
