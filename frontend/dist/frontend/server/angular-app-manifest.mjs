
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
    "route": "/history"
  },
  {
    "renderMode": 2,
    "redirectTo": "/",
    "route": "/**"
  }
],
  entryPointToBrowserMapping: undefined,
  assets: {
    'index.csr.html': {size: 1656, hash: 'f560b4dd4ebc4db262bf1a71686a89347c39a706d8dd73eeed2198511a7218b3', text: () => import('./assets-chunks/index_csr_html.mjs').then(m => m.default)},
    'index.server.html': {size: 2169, hash: 'e9346d0eebc683303c59b54572b73d7b55c20118a42cddb3c2f9b87cbeabac8e', text: () => import('./assets-chunks/index_server_html.mjs').then(m => m.default)},
    'dashboard/index.html': {size: 5584, hash: 'c5da9191014bf318a052e71633b17b29f642a6e4774ed453ef47c2f20a8763d9', text: () => import('./assets-chunks/dashboard_index_html.mjs').then(m => m.default)},
    'history/index.html': {size: 5849, hash: '9e87ce215f7517716b75a015423fdc2fe35ff2bc6d712c97a77b0defac18d6cf', text: () => import('./assets-chunks/history_index_html.mjs').then(m => m.default)},
    'sentiment/index.html': {size: 6954, hash: '252b67a49298c562a234b88d3884c8742b3a74c57d5871f3f35f9b769e6c4448', text: () => import('./assets-chunks/sentiment_index_html.mjs').then(m => m.default)},
    'portfolio/index.html': {size: 6928, hash: '07e0d7f720dc67695e922dd26ff251faab97ad23128ff9e4431c41e4e2ccc35e', text: () => import('./assets-chunks/portfolio_index_html.mjs').then(m => m.default)},
    'index.html': {size: 5577, hash: '664203b5262fd73761c4777da70a2b71f8d999c73c7dbc508abfaa01fd24a153', text: () => import('./assets-chunks/index_html.mjs').then(m => m.default)},
    'options/index.html': {size: 8171, hash: 'ca80d9a16c1408591e6e3dc4b5b33f7af237075464b4677b31e424250de9ed3f', text: () => import('./assets-chunks/options_index_html.mjs').then(m => m.default)},
    'styles-5INURTSO.css': {size: 0, hash: 'menYUTfbRu8', text: () => import('./assets-chunks/styles-5INURTSO_css.mjs').then(m => m.default)}
  },
};
