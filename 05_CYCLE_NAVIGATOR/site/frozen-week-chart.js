/* TradingView Lightweight Charts 5.2.0. Presentation only; never changes source data. */
(() => {
  'use strict';
  const DAY=86400000,BLUE='#5f96ff',GREEN='#27c59a';
  let instance=null,asset='BTC',selected=null;
  const txt=(en,da)=>window.CNI18n?.language==='da'?da:en;
  const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num=v=>typeof v==='number'&&Number.isFinite(v)&&v>0;
  const money=v=>num(v)?'$'+v.toLocaleString(window.CNI18n?.language==='da'?'da-DK':'en-US',{minimumFractionDigits:2,maximumFractionDigits:2}):'—';
  const stamp=t=>new Date(t).toLocaleString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZone:'UTC'})+' UTC';
  function model(data,key,now=Date.now()){
    const live=data?.public_live_precision,current=data?.public_series?.current_public_projection||{};
    if(live?.contract!=='CN_PUBLIC_LIVE_PRICE_PRECISION_v1'||live.public_issue_number!==current.public_issue_number||live.forecast_week!==current.forecast_week)return null;
    const windows=['day_1_2','day_3_4','day_5_7'],summary=live.window_scores||{};
    const start=Date.parse(summary.day_1_2?.window_start_utc),end=Date.parse(summary.day_5_7?.window_end_utc);
    if(!Number.isFinite(start)||end-start!==7*DAY)return null;
    const rows=windows.map(w=>(live.rows||[]).find(r=>r.asset===key&&r.window===w));
    if(rows.some(r=>!r||!num(r.forecast_low)||!num(r.forecast_high)||r.forecast_low>=r.forecast_high))return null;
    const obs=live.daily_observations?.contract==='CN_PUBLIC_DAILY_OBSERVATIONS_v1'?live.daily_observations:null;
    const cutoff=Date.parse(obs?.observed_through_utc||live.live_as_of_utc),age=now-cutoff;
    const stale=!Number.isFinite(cutoff)||age<0||age>Math.max(30,Number(live.freshness_sla_minutes)||90)*60000;
    const freeze=live.daily_price_path,raw=freeze?.contract==='CN_FROZEN_DAILY_PRICE_PATH_v1'&&freeze.forecast_week===live.forecast_week&&freeze[key]?.status==='PUBLISHED'?freeze[key].points:[];
    const daily=Array.isArray(raw)&&raw.length===7&&raw.every((p,i)=>p.day===i+1&&[p.low,p.high,p.expected_close].every(num)&&p.low<p.high&&p.low<=p.expected_close&&p.expected_close<=p.high)?raw:[];
    const days=Array.from({length:7},(_,i)=>{
      const d=start+i*DAY,p=obs?.[key]?.find(p=>p.day===i+1),asOf=Date.parse(p?.as_of_utc);
      // Exact existing UTC-day eligibility. An incomplete day never becomes a settled close.
      const actual=p&&p.date===new Date(d).toISOString().slice(0,10)&&p.coverage_complete_to_date===true&&asOf>d&&asOf<=d+DAY&&asOf<=cutoff&&asOf<=now&&[p.low,p.high,p.close].every(num)&&p.low<=p.close&&p.close<=p.high?p:null;
      return {date:new Date(d).toISOString().slice(0,10),time:d/1000,index:i,forecast:daily[i]||null,range:rows[i<2?0:i<4?1:2],actual};
    });
    return {live,start,end,cutoff,stale,days,daily,rows,summary,windows};
  }
  // A series primitive uses only public coordinate APIs. Forecast geometry is never a fitted curve.
  class EvidenceOverlay {
    constructor(m,series){this.m=m;this.series=series;this.view={zOrder:()=> 'bottom',renderer:()=>({draw:target=>target.useMediaCoordinateSpace(scope=>this.draw(scope))})};}
    attached({chart,requestUpdate}){this.chart=chart;this.requestUpdate=requestUpdate;requestUpdate();}
    detached(){this.chart=null;}
    paneViews(){return [this.view];}
    updateAllViews(){}
    draw({context:c,mediaSize:size}){
      if(!this.chart)return; const x=t=>this.chart.timeScale().timeToCoordinate(t),y=v=>this.series.priceToCoordinate(v),m=this.m;
      c.save();
      if(m.daily.length){
        const upper=m.days.map(d=>[x(d.time),y(d.forecast.high)]),lower=m.days.map(d=>[x(d.time),y(d.forecast.low)]).reverse();
        if(upper.concat(lower).every(p=>p.every(v=>v!==null))){c.beginPath();upper.concat(lower).forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.closePath();c.fillStyle='rgba(95,150,255,.09)';c.fill();}
      }else{
        m.rows.forEach((r,i)=>{
          const first=i===0?0:i===1?2:4,last=i===0?1:i===1?3:6;
          const left=x(m.days[first].time),right=x(m.days[last].time),next=x(m.days[Math.min(first+1,6)].time),step=(next??0)-(left??0)||40;
          const top=y(r.forecast_high),bottom=y(r.forecast_low);
          if([left,right,top,bottom].some(v=>v===null))return;
          const l=Math.max(0,left-step*.5),rr=Math.min(size.width,right+step*.5);
          c.fillStyle='rgba(95,150,255,.085)';c.fillRect(l,top,rr-l,bottom-top);
          c.strokeStyle='rgba(95,150,255,.38)';c.lineWidth=1;c.setLineDash([4,4]);
          c.beginPath();c.moveTo(l,top);c.lineTo(rr,top);c.moveTo(l,bottom);c.lineTo(rr,bottom);c.stroke();c.setLineDash([]);
        });
      }
      const last=m.days.filter(d=>d.actual).at(-1);
      if(last){const xx=x(last.time);if(xx!==null){c.fillStyle='rgba(160,177,198,.035)';c.fillRect(xx,0,size.width-xx,size.height);c.strokeStyle='rgba(160,177,198,.22)';c.setLineDash([3,5]);c.beginPath();c.moveTo(xx,0);c.lineTo(xx,size.height);c.stroke();c.setLineDash([]);}}
      m.days.forEach(d=>{if(!d.actual)return;const xx=x(d.time),hi=y(d.actual.high),lo=y(d.actual.low);if([xx,hi,lo].some(v=>v===null))return;c.strokeStyle='rgba(39,197,154,.48)';c.lineWidth=1;c.beginPath();c.moveTo(xx,hi);c.lineTo(xx,lo);c.moveTo(xx-3,hi);c.lineTo(xx+3,hi);c.moveTo(xx-3,lo);c.lineTo(xx+3,lo);c.stroke();});c.restore();
    }
  }
  function mount(host,data){
    if(instance){instance.chart?.remove();instance=null;}
    if(!host)return;
    const m=model(data,asset);if(!m){host.innerHTML='<p>'+txt('Frozen weekly data unavailable.','Frosne ugedata er ikke tilgængelige.')+'</p>';return;}
    const lib=window.LightweightCharts;
    const last=m.days.filter(d=>d.actual).at(-1),picked=m.days.find(d=>d.index===selected)||last||m.days[0];selected=picked.index;
    const rangeLabel=new Date(m.start).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{day:'numeric',month:'short',timeZone:'UTC'})+' – '+new Date(m.end-DAY).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{day:'numeric',month:'short',timeZone:'UTC'});
    host.innerHTML='<div class="fw-toolbar"><div class="fw-assets" role="group" aria-label="'+txt('Chart asset','Grafens aktiv')+'">'+['BTC','ETH'].map(k=>'<button type="button" data-fw-asset="'+k+'" aria-pressed="'+(k===asset)+'">'+k+'</button>').join('')+'</div><span class="fw-period">1W <i>·</i> '+rangeLabel+'</span><button type="button" class="fw-reset" aria-label="'+txt('Reset chart view','Nulstil grafvisning')+'">↔</button></div><div class="fw-quote"><div><span>'+asset+' / USD</span><strong>'+money(last?.actual?.close)+'</strong></div><div class="fw-source"><span class="'+(m.stale?'stale':'fresh')+'">'+txt(m.stale?'STALE SNAPSHOT':'OBSERVED',m.stale?'FORÆLDET ØJEBLIKSBILLEDE':'OBSERVERET')+'</span><small>'+escape(Number.isFinite(m.cutoff)?stamp(m.cutoff):txt('No observation time','Intet observationstidspunkt'))+'</small></div></div><div class="fw-legend"><span><i class="forecast"></i>'+txt(m.daily.length?'Frozen forecast + range':'Frozen forecast range',m.daily.length?'Frossen prognose + interval':'Frossent prognoseinterval')+'</span><span><i class="actual"></i>'+txt('Observed price + low/high','Observeret pris + lav/høj')+'</span></div><div class="fw-canvas" role="img" aria-label="'+txt('Frozen weekly forecast and observed daily prices. Future observations are empty.','Frossen ugeprognose og observerede dagspriser. Fremtidige observationer er tomme.')+'"></div><div class="fw-days" role="group" aria-label="'+txt('Select UTC day','Vælg UTC-dag')+'">'+m.days.map(d=>'<button type="button" data-fw-day="'+d.index+'" aria-pressed="'+(picked.index===d.index)+'">'+new Date(d.time*1000).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'short',timeZone:'UTC'})+'<small>'+new Date(d.time*1000).getUTCDate()+'</small></button>').join('')+'</div><div class="fw-readout" aria-live="polite"></div><div class="fw-note">'+txt(m.daily.length?'Straight lines connect published daily points. They do not describe intraday movement.':'This week was frozen as three range windows. A daily forecast line was not published.',m.daily.length?'Rette linjer forbinder de offentliggjorte dagspunkter. De beskriver ikke dagens kursbevægelser.':'Denne uge blev fastlåst som tre prisintervaller. Der er ikke offentliggjort en daglig prognoselinje.')+'</div><div class="fw-footer"><span>'+txt('Frozen before outcomes','Fastlåst før udfald')+' · CN #'+m.live.public_issue_number+'</span><a href="https://www.tradingview.com/" target="_blank" rel="noopener">TradingView Lightweight Charts™</a></div><div class="fw-attribution" data-no-translate>Copyright (с) 2025 TradingView, Inc.</div>';
    function readout(d){
      const f=d.forecast,p=d.actual,r=d.range;
      host.querySelectorAll('[data-fw-day]').forEach(b=>b.setAttribute('aria-pressed',Number(b.dataset.fwDay)===d.index));
      const delta=p&&f&&p.status==='COMPLETE'?((p.close/f.expected_close-1)*100).toLocaleString(window.CNI18n?.language==='da'?'da-DK':'en-US',{maximumFractionDigits:2,signDisplay:'always'})+'%':null;
      host.querySelector('.fw-readout').innerHTML='<div class="fw-day-status"><strong>'+escape(new Date(d.time*1000).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'}))+'</strong><span>'+txt(p?(p.status==='COMPLETE'?'CLOSED':'DAY STILL OPEN'):'NO COMPLETE OBSERVATION',p?(p.status==='COMPLETE'?'AFSLUTTET':'DAGEN ER STADIG ÅBEN'):'INGEN KOMPLET OBSERVATION')+'</span></div><div class="fw-values"><div><span>'+txt(f?'Expected close':'Frozen interval',f?'Forventet lukkepris':'Frossent interval')+'</span><strong>'+escape(f?money(f.expected_close):money(r.forecast_low)+' – '+money(r.forecast_high))+'</strong>'+(f?'<small>'+money(f.low)+' – '+money(f.high)+'</small>':'')+'</div><div><span>'+txt('Observed price','Observeret pris')+'</span><strong class="fw-green">'+money(p?.close)+'</strong><small>'+txt(p?'Low / high':'No price plotted',p?'Lav / høj':'Ingen pris tegnet')+(p?' '+money(p.low)+' – '+money(p.high):'')+'</small></div></div><p>'+escape(delta?txt('Closing deviation: ','Afvigelse ved lukning: ')+delta:p&&f?txt('Closing deviation pending until this UTC day closes.','Afvigelse ved lukning afventer, at UTC-dagen afsluttes.'):txt('Only published observations are shown. Missing coverage remains empty.','Kun offentliggjorte observationer vises. Manglende dækning forbliver tom.'))+'</p>'+(p?'<small>'+escape(stamp(Date.parse(p.as_of_utc)))+' · '+p.observed_hours+' '+txt('observed hours','observerede timer')+'</small>':'');
    }
    readout(picked);
    host.querySelectorAll('[data-fw-day]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.fwDay);readout(m.days[selected]);});
    host.querySelectorAll('[data-fw-asset]').forEach(b=>b.onclick=()=>{asset=b.dataset.fwAsset;mount(host,data);});
    if(!lib){host.querySelector('.fw-canvas').innerHTML='<p>'+txt('Chart could not load. Exact values remain available below.','Grafen kunne ikke indlæses. Præcise værdier er stadig tilgængelige nedenfor.')+'</p>';return;}
    const canvas=host.querySelector('.fw-canvas');
    const values=[...m.rows.flatMap(r=>[r.forecast_low,r.forecast_high]),...m.daily.flatMap(p=>[p.low,p.high]),...m.days.filter(d=>d.actual).flatMap(d=>[d.actual.low,d.actual.high])];
    const min=Math.min(...values),max=Math.max(...values),padding=(max-min)*.10;
    const chart=lib.createChart(canvas,{autoSize:true,layout:{background:{type:lib.ColorType.Solid,color:'#0d1b2c'},textColor:'#91a2b9',fontFamily:'-apple-system,BlinkMacSystemFont,system-ui,sans-serif',fontSize:11,attributionLogo:true},grid:{vertLines:{color:'rgba(147,166,190,.055)'},horzLines:{color:'rgba(147,166,190,.09)'}},rightPriceScale:{borderColor:'#243247',minimumWidth:72,scaleMargins:{top:.13,bottom:.13}},timeScale:{borderColor:'#243247',timeVisible:false,rightOffset:.5,fixLeftEdge:true,fixRightEdge:true,lockVisibleTimeRangeOnResize:true,tickMarkFormatter:time=>new Date(typeof time==='number'?time*1000:time).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'short',timeZone:'UTC'})},crosshair:{mode:lib.CrosshairMode.Normal,vertLine:{color:'#6b809b',width:1,style:lib.LineStyle.Dashed,labelBackgroundColor:'#30435d'},horzLine:{color:'#6b809b',width:1,style:lib.LineStyle.Dashed,labelBackgroundColor:'#30435d'}},localization:{locale:window.CNI18n?.language==='da'?'da-DK':'en-US',priceFormatter:money,timeFormatter:t=>new Date(t*1000).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'})},handleScroll:{mouseWheel:false,pressedMouseMove:true,horzTouchDrag:true,vertTouchDrag:false},handleScale:{mouseWheel:true,pinch:true,axisPressedMouseMove:{time:true,price:true}}});
    const opts={priceLineVisible:false,lastValueVisible:false,crosshairMarkerVisible:true,lineWidth:2,autoscaleInfoProvider:()=>({priceRange:{minValue:min-padding,maxValue:max+padding}})};
    const baseline=chart.addSeries(lib.LineSeries,{...opts,color:BLUE,lineType:lib.LineType.Simple});baseline.setData(m.days.map(d=>d.forecast?{time:d.time,value:d.forecast.expected_close}:{time:d.time}));
    const scaleAnchor=chart.addSeries(lib.LineSeries,{...opts,color:'transparent',lineVisible:false,crosshairMarkerVisible:false});scaleAnchor.setData(m.days.map(d=>({time:d.time,value:d.forecast?.high??d.range.forecast_high})));
    scaleAnchor.attachPrimitive(new EvidenceOverlay(m,scaleAnchor));
    // Separate observed runs rather than trusting a line to bridge missing evidence.
    let run=[];const runs=[];m.days.forEach(d=>{if(d.actual)run.push(d);else if(run.length){runs.push(run);run=[];}});if(run.length)runs.push(run);
    runs.forEach((points,i)=>{const series=chart.addSeries(lib.LineSeries,{...opts,color:GREEN,lineWidth:2,pointMarkersVisible:true,pointMarkersRadius:3,lastValueVisible:i===runs.length-1,priceLineVisible:i===runs.length-1,priceLineColor:'rgba(39,197,154,.30)',priceLineStyle:lib.LineStyle.Dashed});series.setData(points.map(d=>({time:d.time,value:d.actual.close})));});
    chart.timeScale().setVisibleLogicalRange({from:-.65,to:6.65});
    const select=d=>{selected=d.index;readout(d);};
    chart.subscribeCrosshairMove(p=>{if(p.time===undefined)return;const d=m.days.find(d=>d.time===p.time);if(d)select(d);});
    chart.subscribeClick(p=>{if(p.time===undefined)return;const d=m.days.find(d=>d.time===p.time);if(d)select(d);});
    host.querySelectorAll('[data-fw-day]').forEach(b=>b.onclick=()=>select(m.days[Number(b.dataset.fwDay)]));
    host.querySelectorAll('[data-fw-asset]').forEach(b=>b.onclick=()=>{asset=b.dataset.fwAsset;mount(host,data);});
    host.querySelector('.fw-reset').onclick=()=>chart.timeScale().setVisibleLogicalRange({from:-.65,to:6.65});
    instance={chart,host,data};
  }
  window.CNWeekChart={mount,model};
  document.addEventListener('cn-language-change',()=>{if(instance?.host.isConnected)mount(instance.host,instance.data);});
})();
