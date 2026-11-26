import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { hubAutocompleteDefaults } from "./config/vuetifyDefaults";

// O dayjs publicado e CJS (UMD em dayjs.min.js). Com rolldown-vite o otimizador
// nao faz o pre-bundle dele e o browser/SSR recebem o arquivo cru, quebrando com
// "does not provide an export named 'default'". Aliases para o build ESM oficial
// do proprio dayjs resolvem isso. Caminhos absolutos: rolldown-vite nao expande
// capturas ($1) em alias, entao os plugins sao mapeados um a um.
const require = createRequire(import.meta.url);
const dayjsRoot = require
  .resolve("dayjs/package.json")
  .replace(/[\\/]package\.json$/, "")
  .replace(/\\/g, "/");
const dayjsEsm = `${dayjsRoot}/esm`;
const dayjsPlugins = [
  "advancedFormat",
  "customParseFormat",
  "dayOfYear",
  "isSameOrAfter",
  "isSameOrBefore",
  "localeData",
  "quarterOfYear",
  "weekOfYear",
  "weekYear",
];

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: false },
  ssr: false,
  serverDir: fileURLToPath(new URL("./server",import.meta.url)),
  nitro: { preset: process.env.VERCEL ? "vercel" : "node-server" },
  modules: [
    "@pinia/nuxt",
    "vuetify-nuxt-module",
  ],
  components: [{ path: "~/components", pathPrefix: true }],
  css: [
    "~/assets/css/main.css",
    "~/assets/css/vuetify-hub.css",
    "~/assets/css/typography.css",
    "~/assets/css/central-overrides.css",
  ],
  vuetify: {
    moduleOptions: {
      styles: true,
      // Evita sobrescrever o useLayout nativo do Nuxt.
      prefixComposables: ["useLayout"],
    },
    vuetifyOptions: {
      theme: {
        defaultTheme: "light",
        themes: {
          light: {
            dark: false,
            colors: {
              background: "#f4f5f7",
              surface: "#ffffff",
              primary: "#304f7e",
              "primary-darken-1": "#213758",
              secondary: "#6b7280",
              "secondary-darken-1": "#4b5563",
              accent: "#eaa239",
              error: "#c0392b",
              info: "#007cc5",
              success: "#609346",
              warning: "#eaa239",
            },
          },
          dark: {dark:true,colors:{background:"#121418",surface:"#1b1f24",primary:"#93b5e5",secondary:"#9ca3af",accent:"#eaa239",error:"#f06b78",info:"#66a8ff",success:"#75c65f",warning:"#eaa239"}},
        },
      },
      icons: {
        defaultSet: "mdi-svg",
      },
      locale: {
        locale: "pt",
        fallback: "en",
      },
      localeMessages: ["en", "pt"],
      defaults: {
        VBtn: {
          // Ações neutras são secundárias por padrão. Ações semânticas
          // (salvar, aprovar, excluir, importar etc.) declaram a cor no uso.
          color: "secondary",
          variant: "outlined",
          rounded: "lg",
          elevation: 0,
        },
        VAlert: {
          density: "compact",
          border: "start",
          rounded: "lg",
        },
        VCard: { rounded: "lg", elevation: 0 },
        VTextField: {
          variant: "outlined",
          density: "comfortable",
          hideDetails: "auto",
        },
        VTextarea: {
          variant: "outlined",
          density: "comfortable",
          hideDetails: "auto",
        },
        VSelect: {
          variant: "outlined",
          density: "comfortable",
          hideDetails: "auto",
        },
        VAutocomplete: hubAutocompleteDefaults,
      },
    },
  },
  vite: {
    resolve: {
      alias: [
        { find: /^dayjs$/, replacement: `${dayjsEsm}/index.js` },
        ...dayjsPlugins.map((plugin) => ({
          find: `dayjs/plugin/${plugin}.js`,
          replacement: `${dayjsEsm}/plugin/${plugin}/index.js`,
        })),
        // Imports sem sufixo .js caem no diretorio do plugin (resolver pega o index.js).
        { find: /^dayjs\/plugin\//, replacement: `${dayjsEsm}/plugin/` },
        { find: /^dayjs\/locale\//, replacement: `${dayjsEsm}/locale/` },
      ],
    },
  },
  runtimeConfig: { apiBase: process.env.NUXT_API_BASE || process.env.NUXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api/v1", public:{apiBase:"http://127.0.0.1:8000/api/v1"} },
  typescript: {
    strict: true,
    // A validação roda explicitamente em `pnpm typecheck`. Evita que o build
    // dispare uma segunda instância do vue-tsc com argumentos conflitantes.
    typeCheck: false,
  },
  app: {
    head: {
      htmlAttrs: { lang: "pt-BR" },
      title: "Nexotiva | Central de Chamados",
      meta: [
        { name: "description", content: "Central de atendimento Nexotiva." },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "theme-color", content: "#304f7e" },
      ],
      link: [
        { rel: "icon", type: "image/png", href: "/brand/logo.png" },
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "anonymous" },
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=Manrope:wght@200..800&display=swap",
        },
      ],
    },
  },
});
