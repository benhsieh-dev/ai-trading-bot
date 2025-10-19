
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
    "route": "/portfolio"
  },
  {
    "renderMode": 2,
    "route": "/options"
  },
  {
    "renderMode": 2,
    "redirectTo": "/",
    "route": "/**"
  }
],
  entryPointToBrowserMapping: undefined,
  assets: {
    'index.csr.html': {size: 492, hash: 'c5b5266519d73f91a00808761ca2eb03b2ace0be16916ebfd4e184ab92cd39c2', text: () => import('./assets-chunks/index_csr_html.mjs').then(m => m.default)},
    'index.server.html': {size: 1005, hash: '9955ca7b5cc8dca92b748b24b0d7e9aac39c863a0e385c63f9b14c76b46e3f66', text: () => import('./assets-chunks/index_server_html.mjs').then(m => m.default)},
    'dashboard/index.html': {size: 4136, hash: '621813312969a67f813ec3cd0ae4d3efaaa2c339a8d735fff6ab27092d5b6f10', text: () => import('./assets-chunks/dashboard_index_html.mjs').then(m => m.default)},
    'portfolio/index.html': {size: 4218, hash: 'd36a2ebffbdfc9bd92261fb34c2cc1f18a5c7917095dfb1d5b78f1bbc6975d12', text: () => import('./assets-chunks/portfolio_index_html.mjs').then(m => m.default)},
    'options/index.html': {size: 6723, hash: 'f93e6049edd813973183338e84b61bf2f5d4810d1feffdbbf526d89033d9b08d', text: () => import('./assets-chunks/options_index_html.mjs').then(m => m.default)},
    'index.html': {size: 4129, hash: 'a214c74bb33b8e97e43c3df4d6f7553cb331c3a540d71ba222d97683aea91047', text: () => import('./assets-chunks/index_html.mjs').then(m => m.default)},
    'styles-5INURTSO.css': {size: 0, hash: 'menYUTfbRu8', text: () => import('./assets-chunks/styles-5INURTSO_css.mjs').then(m => m.default)}
  },
};
