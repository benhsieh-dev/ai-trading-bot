export default `<!DOCTYPE html><html lang="en" data-beasties-container><head>
  <meta charset="utf-8">
  <title>AI Trading Bot Dashboard</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">

  <!-- Open Graph Meta Tags -->
  <meta property="og:title" content="AI Trading Bot Dashboard">
  <meta property="og:description" content="Test AI sentiment analysis vs traditional investing strategies with real-time trading simulation">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://ai-trading-bot-a0j9.onrender.com/">
  <meta property="og:image" content="https://ai-trading-bot-a0j9.onrender.com/static/image/og-image.png">
  <meta property="og:image:width" content="4047">
  <meta property="og:image:height" content="2118">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:alt" content="AI Trading Bot Dashboard - Sentiment Analysis vs Traditional Investing">

  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="AI Trading Bot Dashboard">
  <meta name="twitter:description" content="Test AI sentiment analysis vs traditional investing strategies with real-time trading simulation">
  <meta name="twitter:image" content="https://ai-trading-bot-a0j9.onrender.com/static/image/og-image.png">
<link rel="stylesheet" href="styles-5INURTSO.css"><style ng-app-id="ng">.navigation-tabs{display:flex;background-color:#f8f9fa;border-bottom:2px solid #e9ecef;padding:0;margin:0;box-shadow:0 2px 4px #0000001a}.nav-tab{padding:12px 24px;text-decoration:none;color:#6c757d;font-weight:500;border-bottom:3px solid transparent;transition:all .3s ease;background-color:transparent;border-radius:0}.nav-tab:hover{color:#495057;background-color:#e9ecef}.nav-tab.active{color:#007bff;border-bottom-color:#007bff;background-color:#fff}.nav-tab.disabled{color:#adb5bd;cursor:not-allowed;opacity:.6}.nav-tab.disabled:hover{background-color:transparent;color:#adb5bd}
</style><style ng-app-id="ng">.dashboard-grid[_ngcontent-ng-c1259898447]{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem;padding:1rem}.status-card[_ngcontent-ng-c1259898447], .sentiment-card[_ngcontent-ng-c1259898447], .controls-card[_ngcontent-ng-c1259898447]{border:1px solid #ddd;border-radius:8px;padding:1rem;background-color:#f9f9f9}.controls-card[_ngcontent-ng-c1259898447]   input[_ngcontent-ng-c1259898447]{margin-right:.5rem;padding:.5rem;border:1px solid #ccc;border-radius:4px}.controls-card[_ngcontent-ng-c1259898447]   button[_ngcontent-ng-c1259898447]{margin:.5rem;padding:.5rem 1rem;background:#007bff;color:#fff;border:none;border-radius:4px;cursor:pointer}</style></head>
<body><!--nghm--><script type="text/javascript" id="ng-event-dispatch-contract">(()=>{function p(t,n,r,o,e,i,f,m){return{eventType:t,event:n,targetElement:r,eic:o,timeStamp:e,eia:i,eirp:f,eiack:m}}function u(t){let n=[],r=e=>{n.push(e)};return{c:t,q:n,et:[],etc:[],d:r,h:e=>{r(p(e.type,e,e.target,t,Date.now()))}}}function s(t,n,r){for(let o=0;o<n.length;o++){let e=n[o];(r?t.etc:t.et).push(e),t.c.addEventListener(e,t.h,r)}}function c(t,n,r,o,e=window){let i=u(t);e._ejsas||(e._ejsas={}),e._ejsas[n]=i,s(i,r),s(i,o,!0)}window.__jsaction_bootstrap=c;})();
</script><script>window.__jsaction_bootstrap(document.body,"ng",["click"],[]);</script>
  <app-root ng-version="20.3.4" ngh="1" ng-server-context="ssg"><app-navigation ngh="0"><nav class="navigation-tabs"><a routerlink="/dashboard" routerlinkactive="active" class="nav-tab active" href="/dashboard" jsaction="click:;"> 📈Stock Trading </a><a routerlink="/portfolio" routerlinkactive="active" class="nav-tab" href="/portfolio" jsaction="click:;"> 📊Portfolio</a><a routerlink="/options" routerlinkactive="active" class="nav-tab" href="/options" jsaction="click:;"> 🎯Options Trading </a><a routerlink="/sentiment" routerlinkactive="active" class="nav-tab" href="/sentiment" jsaction="click:;"> 📊Sentiment &amp; Backtesting </a><a routerlink="/history" routerlinkactive="active" class="nav-tab" href="/history" jsaction="click:;"> 🗂️Trade History (PostgreSQL) </a></nav></app-navigation><router-outlet></router-outlet><app-dashboard _nghost-ng-c1259898447 ngh="0"><h1 _ngcontent-ng-c1259898447>🤖AI Trading Bot Dashboard</h1><div _ngcontent-ng-c1259898447 class="dashboard-grid"><div _ngcontent-ng-c1259898447 class="status-card"><h2 _ngcontent-ng-c1259898447>Trading Status</h2><p _ngcontent-ng-c1259898447>Status: Stopped</p><p _ngcontent-ng-c1259898447>Active Symbol: None</p></div><div _ngcontent-ng-c1259898447 class="sentiment-card"><h2 _ngcontent-ng-c1259898447>Market Sentiment</h2><p _ngcontent-ng-c1259898447>Current: Neutral</p><p _ngcontent-ng-c1259898447>Score: N/A</p></div><div _ngcontent-ng-c1259898447 class="controls-card"><h2 _ngcontent-ng-c1259898447>Trading Controls</h2><input _ngcontent-ng-c1259898447 type="text" placeholder="Symbol (e.g., SPY)" value="SPY"><input _ngcontent-ng-c1259898447 type="number" placeholder="Position Size" value="0.5" step="0.1"><button _ngcontent-ng-c1259898447 jsaction="click:;">Start Bot</button><button _ngcontent-ng-c1259898447 jsaction="click:;">Stop Bot</button></div></div></app-dashboard><!----></app-root>
<script src="polyfills-5CFQRCPP.js" type="module"></script><script src="main-6RBCMLV4.js" type="module"></script>

<script id="ng-state" type="application/json">{"__nghData__":[{},{"c":{"1":[{"i":"c1259898447","r":1}]}}]}</script></body></html>`;