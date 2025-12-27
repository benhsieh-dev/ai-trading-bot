
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
    'index.csr.html': {size: 1805, hash: '966b86a8c17dab2999c1c818c472a2aa2dd40c47a6b7c111c41c94086161d278', text: () => import('./assets-chunks/index_csr_html.mjs').then(m => m.default)},
    'index.server.html': {size: 2318, hash: 'd647ffc626d7c0a78193caa6a9203770770decc7344ac422c84530e7617872ab', text: () => import('./assets-chunks/index_server_html.mjs').then(m => m.default)},
    'index.html': {size: 5726, hash: '473cc562f38b1c85ef09b3c33edc5098ebd3d4f233f53b4aeb04c34e68941d5a', text: () => import('./assets-chunks/index_html.mjs').then(m => m.default)},
    'options/index.html': {size: 8320, hash: '76218751c5d3bf457da704e24b9ec24d9a0e7a930d101f050b769a3c237346f4', text: () => import('./assets-chunks/options_index_html.mjs').then(m => m.default)},
    'sentiment/index.html': {size: 7103, hash: '92ed6555002869b009a56b2d3bbe61bda5f67ee6b47280e02e738570a78f0124', text: () => import('./assets-chunks/sentiment_index_html.mjs').then(m => m.default)},
    'portfolio/index.html': {size: 7077, hash: 'f86e96cef83cc63ac2465d04ede9460b5725b289bcc6f6526365abb362f8f528', text: () => import('./assets-chunks/portfolio_index_html.mjs').then(m => m.default)},
    'dashboard/index.html': {size: 5733, hash: '657c855c7bdd455c5fbdbc05ba3091a77b28b50bfafe88f62783140cebb68d2d', text: () => import('./assets-chunks/dashboard_index_html.mjs').then(m => m.default)},
    'history/index.html': {size: 5998, hash: '45a23802087021cf0e123ac5201ad19b5b85d68c10e52aca743622471d5bf781', text: () => import('./assets-chunks/history_index_html.mjs').then(m => m.default)},
    'styles-5INURTSO.css': {size: 0, hash: 'menYUTfbRu8', text: () => import('./assets-chunks/styles-5INURTSO_css.mjs').then(m => m.default)}
  },
};
