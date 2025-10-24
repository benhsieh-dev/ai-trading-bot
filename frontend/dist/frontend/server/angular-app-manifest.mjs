
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
    'index.csr.html': {size: 492, hash: 'c3a507f204541eece77beb42b912083907bb11370e09686673b17d543b13d63e', text: () => import('./assets-chunks/index_csr_html.mjs').then(m => m.default)},
    'index.server.html': {size: 1005, hash: 'f3233737e9f0cf8d29e37739049604f9aaca487b808038e2b4411b50eb404dab', text: () => import('./assets-chunks/index_server_html.mjs').then(m => m.default)},
    'index.html': {size: 4272, hash: '076fca5c3687b0e59bb5b365ecabb27bb2aa9a7eb976f3e3e972e362d0687c35', text: () => import('./assets-chunks/index_html.mjs').then(m => m.default)},
    'portfolio/index.html': {size: 5204, hash: '2fd6cdfff8a2d2bd1a2dc4cea7e5a10027c1f470b641768011399c0c6f5d71f8', text: () => import('./assets-chunks/portfolio_index_html.mjs').then(m => m.default)},
    'options/index.html': {size: 6866, hash: '679bd07085d7f26501412bd20d581e54d4d1267968e73ca29148d2c96c31b691', text: () => import('./assets-chunks/options_index_html.mjs').then(m => m.default)},
    'sentiment/index.html': {size: 5106, hash: 'c63beaa2037335c9b67d14d33e4d26e18590014d03e3a0bd4a7c4c58f2925d62', text: () => import('./assets-chunks/sentiment_index_html.mjs').then(m => m.default)},
    'dashboard/index.html': {size: 4279, hash: '5ef2dfea20c6c50ed40b0132256c68098c9568d898c5d2ebeb0e40d0be75e4fc', text: () => import('./assets-chunks/dashboard_index_html.mjs').then(m => m.default)},
    'styles-5INURTSO.css': {size: 0, hash: 'menYUTfbRu8', text: () => import('./assets-chunks/styles-5INURTSO_css.mjs').then(m => m.default)}
  },
};
