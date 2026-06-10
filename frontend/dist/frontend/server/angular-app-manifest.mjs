
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
    'index.csr.html': {size: 1804, hash: '2cdea894e7b9c7de9aa3a066e311d06c294d367dd43dbf56a8c03a16e5f2ce82', text: () => import('./assets-chunks/index_csr_html.mjs').then(m => m.default)},
    'index.server.html': {size: 2317, hash: '9d6f53c58ae015f47feb4878d25144a247646f4f331c8a86d7750ebbc480bab4', text: () => import('./assets-chunks/index_server_html.mjs').then(m => m.default)},
    'dashboard/index.html': {size: 5732, hash: '03d23eb0df24a73b51b620a8d2603fbeb31fb198a661d1e1e1f4dde96c0bddb8', text: () => import('./assets-chunks/dashboard_index_html.mjs').then(m => m.default)},
    'options/index.html': {size: 8319, hash: '9d0b6d92114766cbfa3264d8b9b8c5d554ebcb1992d41514bad8532f6e57fa93', text: () => import('./assets-chunks/options_index_html.mjs').then(m => m.default)},
    'history/index.html': {size: 5997, hash: '3d5f63b6fafb6c6161b6cef7d9fe21164810f5adee9eb642495c30ff354b175b', text: () => import('./assets-chunks/history_index_html.mjs').then(m => m.default)},
    'index.html': {size: 5725, hash: 'a281dd8d7b2dba67b2d0b6d3c2cb2078620e5a7d65ce585790368b63045f75c6', text: () => import('./assets-chunks/index_html.mjs').then(m => m.default)},
    'portfolio/index.html': {size: 7076, hash: 'aaf2d9341212154e773623508ba64d284400c028a18b1811385aae1ab79323b8', text: () => import('./assets-chunks/portfolio_index_html.mjs').then(m => m.default)},
    'sentiment/index.html': {size: 7102, hash: '771a8b9d8cf99e366171f20428811cdddd1391e053f3f836ce992032b67fb23e', text: () => import('./assets-chunks/sentiment_index_html.mjs').then(m => m.default)},
    'styles-5INURTSO.css': {size: 0, hash: 'menYUTfbRu8', text: () => import('./assets-chunks/styles-5INURTSO_css.mjs').then(m => m.default)}
  },
};
