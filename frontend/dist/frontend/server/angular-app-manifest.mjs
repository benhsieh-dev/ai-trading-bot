
export default {
  bootstrap: () => import('./main.server.mjs').then(m => m.default),
  inlineCriticalCss: true,
  baseHref: '/',
  locale: undefined,
  routes: [
  {
    "renderMode": 2,
    "route": "/"
  },
  {
    "renderMode": 2,
    "route": "/dashboard"
  },
  {
    "renderMode": 2,
    "route": "/options"
  },
  {
    "renderMode": 2,
    "route": "/portfolio"
  },
  {
    "renderMode": 2,
    "route": "/sentiment"
  },
  {
    "renderMode": 2,
    "redirectTo": "/",
    "route": "/**"
  }
],
  entryPointToBrowserMapping: undefined,
  assets: {
    'index.csr.html': {size: 492, hash: 'ffdb94a5b10eea15227ba0b4afcbed435aea69795e3e9fcf3e99cb47d3c4c1ea', text: () => import('./assets-chunks/index_csr_html.mjs').then(m => m.default)},
    'index.server.html': {size: 1005, hash: '00245c3d18e49a688375af688d54a9fbcd43b1598959cf43407397582b39b05a', text: () => import('./assets-chunks/index_server_html.mjs').then(m => m.default)},
    'index.html': {size: 4272, hash: 'ba32f814663e1e1bb23350b10f2544d6b92df5cd0188ad3e2d1a03cc2a03042f', text: () => import('./assets-chunks/index_html.mjs').then(m => m.default)},
    'portfolio/index.html': {size: 5204, hash: '940a16367148939cbeec5957c6adfa002a65786b8480bb0d71a0297cdfeb7f09', text: () => import('./assets-chunks/portfolio_index_html.mjs').then(m => m.default)},
    'sentiment/index.html': {size: 5649, hash: 'd157f062f08f18f51bded3815c6f6aecb43ce939d38aff3303016e0796cfdb3f', text: () => import('./assets-chunks/sentiment_index_html.mjs').then(m => m.default)},
    'dashboard/index.html': {size: 4279, hash: 'a1c860154a8aa647a18ac561598c7eba805bfbbcb2ae3fa8f4f00e123aa43b44', text: () => import('./assets-chunks/dashboard_index_html.mjs').then(m => m.default)},
    'options/index.html': {size: 6866, hash: '5c571935ae82f00cfeb2179c873f6cf23a3d4f4adf99b59e5b9fde0f9ff96ed4', text: () => import('./assets-chunks/options_index_html.mjs').then(m => m.default)},
    'styles-5INURTSO.css': {size: 0, hash: 'menYUTfbRu8', text: () => import('./assets-chunks/styles-5INURTSO_css.mjs').then(m => m.default)}
  },
};
