// QA-only DOM probe. Creates an instrumented *copy* of the already built
// offline HTML, never modifies the download artifact or production files.
// Used with stock headless Chrome in the existing PR smoke-check workflow.
import { readFileSync, writeFileSync } from 'node:fs';
if(process.argv.length!==4) throw new Error('Usage: node prepare-browser-qa.mjs <offline.html> <qa.html>');
const input=readFileSync(process.argv[2],'utf8');
if(!input.includes('cn-path-week')||!input.includes('data:application/json;base64,'))
  throw new Error('Refusing QA of an unexpected/unbound HTML file');
const script=String.raw`<script>
(function(){
  let polls=0;
  function check(){
    const target=document.getElementById('cn-path-week');
    const svg=document.querySelector('.cn-history-chart');
    if(!target || !svg) {
      if(++polls < 100) return setTimeout(check,35);
      document.documentElement.setAttribute('data-cn-qa-ready','FAIL');
      return;
    }
    setTimeout(()=>{
      const forecast=svg.querySelector('.cn-chart-forecast-midpoint');
      const actual=svg.querySelector('.cn-chart-close-path');
      const rect=target.getBoundingClientRect();
      const firstTop=Math.round(rect.top);
      const targetRouted=location.hash==='#cn-path-week' &&
        firstTop>=-160 && firstTop<=180;
      const sourceLines=Boolean(forecast?.getAttribute('d')?.length>30 &&
        actual?.getAttribute('d')?.length>30);
      const overflow=document.documentElement.scrollWidth>window.innerWidth+1;
      document.documentElement.setAttribute('data-cn-qa-ready',sourceLines?'PASS':'FAIL');
      document.documentElement.setAttribute('data-cn-qa-deeplink',targetRouted?'PASS':'FAIL');
      document.documentElement.setAttribute('data-cn-qa-overflow',overflow?'FAIL':'PASS');
      document.documentElement.setAttribute('data-cn-qa-viewport',String(window.innerWidth));
      document.documentElement.setAttribute('data-cn-qa-original-top',String(firstTop));
      // Always capture the target graph, not the unrelated Overview card.
      target.scrollIntoView({behavior:'auto',block:'start'});
    },450);
  }
  setTimeout(check,60);
})();
</script>`;
if(input.split('</body>').length!==2)throw new Error('Unexpected portable HTML structure');
writeFileSync(process.argv[3],input.replace('</body>',()=>script+'</body>'));
