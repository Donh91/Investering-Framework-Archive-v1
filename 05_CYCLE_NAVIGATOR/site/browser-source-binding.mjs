// Source-bound real-browser QA; evidence only, never market or deploy authority.
const criticalData=['data/latest.json','data/compass.json','history-scoreboard.json'];

export function requiredBrowserAssets(indexHtml){
  if(typeof indexHtml!=='string'||!indexHtml.includes('<html'))throw Error('BUILD_INDEX_UNAVAILABLE');
  const required=new Set(['index.html','market-compass-premium.js','public-product.js','i18n-da.json',...criticalData]);
  for(const match of indexHtml.matchAll(/<(?:script|link)\b[^>]*\b(?:src|href)\s*=\s*["']([^"']+)["']/gi)){
    const raw=match[1].split(/[?#]/,1)[0];
    if(/^\.\/[A-Za-z0-9_./-]+\.(?:js|css)$/.test(raw)&&!raw.includes('..'))required.add(raw.slice(2));
  }
  return [...required].sort();
}

export function firstPartySourceFile(url,base){
  let u,origin;
  try{u=new URL(url);origin=new URL(base);}catch{return null;}
  if(u.origin!==origin.origin)return null;
  if(u.pathname===origin.pathname)return 'index.html';
  if(!u.pathname.startsWith(origin.pathname))return null;
  let name;
  try{name=decodeURIComponent(u.pathname.slice(origin.pathname.length));}catch{return null;}
  if(!name||name.startsWith('/')||name.split('/').includes('..')||!/^[-A-Za-z0-9_./]+$/.test(name))return null;
  return /\.(?:html|js|css|json|svg|png|webmanifest)$/.test(name)?name:null;
}

export function auditBrowserEvidence(browserSources,required){
  const real=browserSources.filter(c=>!c.synthetic);
  const failures=[],optionalUnavailable=[];
  if(real.length===0)failures.push({error:'NO_REAL_BROWSER_CONTEXTS'});
  const observed=new Set(required);
  for(const context of real){
    const identity=[context.engine,context.width,context.language,context.state].join('/');
    for(const hit of context.responses){if(hit.file)observed.add(hit.file);}
    for(const file of required){
      const hits=context.responses.filter(r=>r.file===file);
      if(hits.length===0||hits.some(r=>r.status!==200||!r.sha256||r.error)){
        failures.push({error:'REQUIRED_SOURCE_NOT_SUCCESSFUL_IN_CONTEXT',context:identity,file});
      }
      if(new Set(hits.filter(r=>r.sha256).map(r=>r.sha256)).size>1){
        failures.push({error:'SOURCE_CHANGED_WITHIN_CONTEXT',context:identity,file});
      }
    }
    for(const hit of context.responses){
      if(required.includes(hit.file))continue;
      if(hit.error||hit.status!==200||!hit.sha256){
        optionalUnavailable.push({context:identity,file:hit.file,status:hit.status??null,error:hit.error||null});
      }
      if(hit.file&&/\.(?:js|css|html)$/.test(hit.file)&&
         (hit.status!==200||!hit.sha256||hit.error)){
        failures.push({error:'RENDERED_STATIC_SOURCE_UNAVAILABLE',context:identity,file:hit.file});
      }
    }
  }
  const files=[...observed].sort(),variants={};
  for(const file of files){
    const hits=real.flatMap(c=>c.responses.filter(r=>r.file===file&&r.status===200&&!r.error&&r.sha256));
    variants[file]=[...new Set(hits.map(r=>r.sha256))];
    // Static sources represent an immutable deployed build, not mutable market data.
    if(/\.(?:html|js|css|svg|png|webmanifest)$/.test(file)&&variants[file].length>1){
      failures.push({error:'MIXED_STATIC_DEPLOYMENT',file});
    }
  }
  return {files,variants,failures,optionalUnavailable,realContextCount:real.length};
}
