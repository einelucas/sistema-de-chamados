// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },

  // Aplicacao interna autenticada, sem necessidade de SEO/SSR. A sessao e guardada em
  // sessionStorage (so existe no navegador), entao o servidor nunca sabe se o usuario esta
  // logado durante a renderizacao SSR -- isso causava um bug real de hidratacao: o servidor
  // renderizava o layout de login (redirecionado pela middleware "auth"), e so depois, no
  // navegador, a sessao era restaurada e a pagina certa era montada por cima, deixando o
  // wrapper do layout errado (".auth-shell") por fora do conteudo real da pagina. Desativar
  // o SSR remove essa classe inteira de bug: a aplicacao roda 100% no navegador.
  ssr: false,

  modules: ["@pinia/nuxt"],

  srcDir: "app/",

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    public: {
      apiBase:
        process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1",
    },
  },

  app: {
    head: {
      title: "Central de Solicitações",
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
          content: "Sistema interno de gerenciamento de solicitações",
        },
      ],
    },
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },
});
