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
    // Observed 1h closes come only from the PUBLIC bounded PASS/OK spot projection.
    // Reject source mismatch/future hours/duplicates/unsorted points; never infer
    // a curve from just window min/max, nor bridge missing UTC hours.
    const h=live.hourly_price_path;
    const hourlyProvenance=h?.contract==='CN_PUBLIC_HOURLY_PRICE_PATH_v1'&&
      h.forecast_week===live.forecast_week&&h.public_issue_number===live.public_issue_number&&
      h.source==='HOURLY_SPOT_PASS_ONLY'&&
      h.semantics==='OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST'&&
      h.observed_through_utc===(obs?.observed_through_utc||live.live_as_of_utc);
    const hourlyRaw=hourlyProvenance?h[key]:null;
    const hourStart=start/1000,hourEnd=end/1000,cutoffSec=cutoff/1000,nowSec=now/1000;
    const validHours=Array.isArray(hourlyRaw)&&hourlyRaw.length<=168&&
      hourlyRaw.every((p,i)=>{
        const time=Date.parse(p?.observed_at_utc)/1000;
        const prev=i?Date.parse(hourlyRaw[i-1]?.observed_at_utc)/1000:-Infinity;
        return typeof p?.observed_at_utc==='string'&&
          /^\d{4}-\d{2}-\d{2}T\d{2}:00:00Z$/.test(p.observed_at_utc)&&
          num(p.close)&&Number.isFinite(time)&&
          time>hourStart&&time<=hourEnd&&time<=cutoffSec&&time<=nowSec&&time>prev;
      });
    const hourly=validHours?hourlyRaw.map(p=>({
      time:Date.parse(p.observed_at_utc)/1000,value:p.close
    })):[];

    const days=Array.from({length:7},(_,i)=>{
      const d=start+i*DAY,p=obs?.[key]?.find(p=>p.day===i+1),asOf=Date.parse(p?.as_of_utc);
      // Exact existing UTC-day eligibility. An incomplete day never becomes a settled close.
      const actual=p&&p.date===new Date(d).toISOString().slice(0,10)&&p.coverage_complete_to_date===true&&asOf>d&&asOf<=d+DAY&&asOf<=cutoff&&asOf<=now&&[p.low,p.high,p.close].every(num)&&p.low<=p.close&&p.close<=p.high?p:null;
      return {date:new Date(d).toISOString().slice(0,10),time:d/1000,closeTime:(d+DAY)/1000,index:i,forecast:daily[i]||null,range:rows[i<2?0:i<4?1:2],actual};
    });
    return {live,start,end,cutoff,stale,days,daily,hourly,rows,summary,windows};
  }
  // Pure drawing plan: exactly one prospective seven-day forecast, and only
  // contiguous observed daily runs. This is independently testable before
  // a future canonical Monday emits its first eligible daily forecast.
  function linePlan(m){
    const forecast=m.daily.length===7
      ?m.days.map(d=>({time:d.closeTime,value:d.forecast.expected_close}))
      :[];
    const actualRuns=[];let current=[];
    if(m.hourly?.length){
      for(const point of m.hourly){
        if(current.length&&point.time-current.at(-1).time!==3600){
          actualRuns.push(current);current=[];
        }
        current.push(point);
      }
    }else{
      m.days.forEach(d=>{
        if(d.actual)current.push({time:Date.parse(d.actual.as_of_utc)/1000,value:d.actual.close});
        else if(current.length){actualRuns.push(current);current=[];}
      });
    }
    if(current.length)actualRuns.push(current);
    return {forecast,actualRuns};
  }
  // Screen-reader contract mirrors what is actually plotted. Source-absent
  // seven-day forecasts are intervals, not a daily forecast curve.
  function graphDescription(m){
    const observed=(m.hourly?.length||0)>0||m.days.some(d=>d.actual);
    const observationCopy=m.hourly?.length
      ?txt('Green solid line: verified hourly closing prices only; missing hours break the line. Measured daily high/low whiskers require complete coverage.',
           'Grøn fuldt optrukken linje: kun verificerede timeslukkepriser; manglende timer afbryder kurven. Dagens høj/lav kræver komplet dækning.')
      :observed
      ?txt('Green solid line: eligible observed daily prices; missing days are unconnected. Measured high/low whiskers are shown only for those observations.',
           'Grøn fuldt optrukken linje: gyldige observerede dagspriser; manglende dage forbindes ikke. Målte lav/høj-markeringer vises kun ved disse observationer.')
      :txt('No eligible observed daily prices yet: no green actual line or measured high/low whiskers are displayed.',
           'Endnu ingen gyldige observerede dagspriser: ingen grøn faktisk kurve eller målte lav/høj-markeringer vises.');
    if(m.daily.length){
      return txt('Blue dotted line: seven original frozen daily expected closing prices, aligned to the end of each UTC day, with original forecast low/high envelope.',
                 'Blå stiplet linje: syv oprindeligt frosne forventede dagslukkepriser placeret ved hver UTC-dags afslutning med oprindeligt lav/høj-prognoseinterval.')
        +' '+observationCopy;
    }
    return txt('No original seven-day closing-price forecast was published. Only three frozen price-range intervals are shown, with no daily forecast line.',
               'Ingen oprindelig syvdagesprognose for dagslukkepriser blev offentliggjort. Kun tre frosne prisintervaller vises uden daglig prognoselinje.')
      +' '+observationCopy;
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
      const spans=m.rows.map((row,index)=>({row,index,first:index===0?0:index===1?2:4,last:index===0?1:index===1?3:6,label:['D1–2','D3–4','D5–7'][index]}));
      c.save();
      if(m.daily.length){
        const upper=m.days.map(d=>[x(d.closeTime),y(d.forecast.high)]),lower=m.days.map(d=>[x(d.closeTime),y(d.forecast.low)]).reverse();
        if(upper.concat(lower).every(p=>p.every(v=>v!==null))){c.beginPath();upper.concat(lower).forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.closePath();c.fillStyle='rgba(95,150,255,.09)';c.fill();}
      }else{
        spans.forEach(({row:r,first,last})=>{
          const left=x(m.days[first].time),right=x(m.days[last].closeTime);
          const top=y(r.forecast_high),bottom=y(r.forecast_low);
          if([left,right,top,bottom].some(v=>v===null))return;
          const l=Math.max(0,left),rr=Math.min(size.width,right);
          const gradient=c.createLinearGradient(0,top,0,bottom);gradient.addColorStop(0,'rgba(95,150,255,.13)');gradient.addColorStop(1,'rgba(95,150,255,.045)');c.fillStyle=gradient;c.fillRect(l,top,rr-l,bottom-top);
          c.strokeStyle='rgba(95,150,255,.44)';c.lineWidth=1;c.setLineDash([4,4]);
          c.beginPath();c.moveTo(l,top);c.lineTo(rr,top);c.moveTo(l,bottom);c.lineTo(rr,bottom);c.stroke();c.setLineDash([]);
        });
      }
      if(!m.daily.length)spans.forEach(({first,last,label},index)=>{
        const left=x(m.days[first].time),right=x(m.days[last].closeTime);
        if(left===null||right===null)return;const l=Math.max(0,left),rr=Math.min(size.width,right),mid=(l+rr)/2;
        if(index){c.strokeStyle='rgba(145,162,185,.14)';c.lineWidth=1;c.setLineDash([2,5]);c.beginPath();c.moveTo(l,8);c.lineTo(l,size.height-22);c.stroke();c.setLineDash([]);}
        c.font='600 9px -apple-system,BlinkMacSystemFont,system-ui,sans-serif';c.textAlign='center';c.textBaseline='middle';const width=c.measureText(label).width+14;c.fillStyle='rgba(20,36,58,.88)';c.fillRect(mid-width/2,9,width,20);c.strokeStyle='rgba(95,150,255,.22)';c.strokeRect(mid-width/2+.5,9.5,width-1,19);c.fillStyle='rgba(181,200,227,.9)';c.fillText(label,mid,19);
      });
      // A vertical marker only denotes the LAST SOURCE OBSERVATION, never a
      // "today" date or an imagined boundary between actual and forecast.
      const last=m.days.filter(d=>d.actual).at(-1),lastTime=m.hourly.at(-1)?.time??(last?Date.parse(last.actual.as_of_utc)/1000:undefined);
      if(lastTime!==undefined){const xx=x(lastTime);if(xx!==null){
        c.fillStyle='rgba(160,177,198,.028)';c.fillRect(xx,0,size.width-xx,size.height);
        c.strokeStyle='rgba(190,205,225,.55)';c.lineWidth=1;c.setLineDash([3,5]);
        c.beginPath();c.moveTo(xx,0);c.lineTo(xx,size.height);c.stroke();c.setLineDash([]);
        const label=txt('LAST SOURCE','SENEST MÅLT');c.font='600 9px -apple-system,BlinkMacSystemFont,system-ui,sans-serif';
        const w=c.measureText(label).width+12;const left=Math.max(0,Math.min(size.width-w,xx-w/2));
        c.fillStyle='rgba(11,26,44,.93)';c.fillRect(left,38,w,18);c.fillStyle='#b6d7ed';
        c.textAlign='center';c.textBaseline='middle';c.fillText(label,left+w/2,47);
      }}
      m.days.forEach(d=>{if(!d.actual)return;const xx=x(Date.parse(d.actual.as_of_utc)/1000),hi=y(d.actual.high),lo=y(d.actual.low);if([xx,hi,lo].some(v=>v===null))return;c.strokeStyle='rgba(39,197,154,.48)';c.lineWidth=1;c.beginPath();c.moveTo(xx,hi);c.lineTo(xx,lo);c.moveTo(xx-3,hi);c.lineTo(xx+3,hi);c.moveTo(xx-3,lo);c.lineTo(xx+3,lo);c.stroke();});c.restore();
    }
  }
  function mount(host,data){
    if(instance){instance.chart?.remove();instance=null;}
    if(!host)return;
    const m=model(data,asset);if(!m){host.innerHTML='<p>'+txt('Frozen weekly data unavailable.','Frosne ugedata er ikke tilgængelige.')+'</p>';return;}
    const lib=window.LightweightCharts;
    const last=m.days.filter(d=>d.actual).at(-1),lastHour=m.hourly.at(-1),picked=m.days.find(d=>d.index===selected)||last||m.days[0];selected=picked.index;
    const rangeLabel=new Date(m.start).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{day:'numeric',month:'short',timeZone:'UTC'})+' – '+new Date(m.end-DAY).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{day:'numeric',month:'short',timeZone:'UTC'});
    host.innerHTML='<div class="fw-toolbar"><div class="fw-assets" role="group" aria-label="'+txt('Chart asset','Grafens aktiv')+'">'+['BTC','ETH'].map(k=>'<button type="button" data-fw-asset="'+k+'" aria-pressed="'+(k===asset)+'">'+k+'</button>').join('')+'</div><span class="fw-period">1W <i>·</i> '+rangeLabel+'</span><button type="button" class="fw-reset" aria-label="'+txt('Reset chart view','Nulstil grafvisning')+'">⌖</button></div><div class="fw-quote"><div><span>'+asset+' / USD · '+txt(m.daily.length?'FORECAST VS ACTUAL':'WEEKLY RANGE ONLY',m.daily.length?'FORECAST VS FAKTISK':'KUN UGEINTERVAL')+'</span><strong>'+money(lastHour?.value??last?.actual?.close)+'</strong></div><div class="fw-source"><span class="'+(m.stale?'stale':'fresh')+'">'+txt(m.stale?'STALE SNAPSHOT':'OBSERVED',m.stale?'FORÆLDET ØJEBLIKSBILLEDE':'OBSERVERET')+'</span><small>'+escape(Number.isFinite(m.cutoff)?stamp(m.cutoff):txt('No observation time','Intet observationstidspunkt'))+'</small></div></div><div class="fw-legend"><span><i class="'+(m.daily.length?'forecast':'interval')+'"></i>'+txt(m.daily.length?'Frozen 7-day forecast · dotted':'Frozen range windows · no daily path',m.daily.length?'Frossen 7-dages prognose · prikket':'Frosne prisintervaller · ingen dagsprognose')+'</span><span><i class="actual"></i>'+txt(m.hourly.length?'Actual hourly closes · solid':'Actual daily closes · solid',m.hourly.length?'Faktiske timesluk · fuld linje':'Faktiske dagsluk · fuld linje')+'</span></div><div class="fw-progress-summary"><span class="fw-progress-actual">'+escape(txt(m.hourly.length?'Verified actual hourly closes: ':'Verified observed days: ',m.hourly.length?'Verificerede faktiske timesluk: ':'Verificerede observationsdage: '))+'<strong>'+(m.hourly.length||m.days.filter(d=>d.actual).length)+'</strong></span><span class="fw-progress-forecast">'+escape(txt(m.daily.length?'7 original forecast closes':'No published daily forecast line',m.daily.length?'7 oprindelige prognosepunkter':'Ingen offentliggjort dagsprognoselinje'))+'</span></div><div class="fw-canvas" role="img" aria-label="'+escape(graphDescription(m))+'"></div><div class="fw-days" role="group" aria-label="'+txt('Select UTC day','Vælg UTC-dag')+'">'+m.days.map(d=>'<button type="button" data-fw-day="'+d.index+'" aria-pressed="'+(picked.index===d.index)+'">'+new Date(d.time*1000).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'short',timeZone:'UTC'})+'<small>'+new Date(d.time*1000).getUTCDate()+'</small></button>').join('')+'</div><div class="fw-readout" aria-live="polite"></div><div class="fw-note">'+txt(m.daily.length?'Dotted forecast covers the original seven UTC daily closes; solid actual follows only eligible observations. No intraday movement implied.':'Only three frozen range windows exist. No authentic daily forecast was published, so no forecast curve is drawn.',m.daily.length?'Den prikkede forecastkurve viser de oprindelige syv UTC-dagspunkter. Den fuldt optrukne faktiske kurve følger kun gyldige observationer. Ingen intradagbevægelse udledes.':'Der findes kun tre frosne prisintervaller. Ingen ægte dagsprognose blev offentliggjort, derfor tegnes ingen forecastkurve.')+'</div><div class="fw-footer"><span>'+txt('Frozen before outcomes','Fastlåst før udfald')+' · CN #'+m.live.public_issue_number+'</span><a href="https://www.tradingview.com/" target="_blank" rel="noopener">TradingView Lightweight Charts™</a></div><div class="fw-attribution" data-no-translate>Copyright (с) 2025 TradingView, Inc.</div>';
    function readout(d){
      const f=d.forecast,p=d.actual,r=d.range;
      const hourCount=m.hourly.filter(x=>x.time>(d.time)&&x.time<=d.time+86400).length;
      host.querySelectorAll('[data-fw-day]').forEach(b=>b.setAttribute('aria-pressed',Number(b.dataset.fwDay)===d.index));
      const delta=p&&f&&p.status==='COMPLETE'?((p.close/f.expected_close-1)*100).toLocaleString(window.CNI18n?.language==='da'?'da-DK':'en-US',{maximumFractionDigits:2,signDisplay:'always'})+'%':null;
      host.querySelector('.fw-readout').innerHTML='<div class="fw-day-status"><strong>'+escape(new Date(d.time*1000).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'}))+'</strong><span>'+txt(p?(p.status==='COMPLETE'?'CLOSED':'DAY STILL OPEN'):'NO COMPLETE OBSERVATION',p?(p.status==='COMPLETE'?'AFSLUTTET':'DAGEN ER STADIG ÅBEN'):'INGEN KOMPLET OBSERVATION')+'</span></div><div class="fw-values"><div><span>'+txt(f?'Expected close':'Frozen interval',f?'Forventet lukkepris':'Frossent interval')+'</span><strong>'+escape(f?money(f.expected_close):money(r.forecast_low)+' – '+money(r.forecast_high))+'</strong>'+(f?'<small>'+money(f.low)+' – '+money(f.high)+'</small>':'')+'</div><div><span>'+txt('Observed price','Observeret pris')+'</span><strong class="fw-green">'+money(p?.close)+'</strong><small>'+txt(p?'Low / high':'No price plotted',p?'Lav / høj':'Ingen pris tegnet')+(p?' '+money(p.low)+' – '+money(p.high):'')+'</small></div></div><p>'+escape(delta?txt('Closing deviation: ','Afvigelse ved lukning: ')+delta:p&&f?txt('Closing deviation pending until this UTC day closes.','Afvigelse ved lukning afventer, at UTC-dagen afsluttes.'):txt('Only published observations are shown. Missing coverage remains empty.','Kun offentliggjorte observationer vises. Manglende dækning forbliver tom.'))+'</p>'+(p?'<small>'+escape(stamp(Date.parse(p.as_of_utc)))+' · '+p.observed_hours+' '+txt('observed hours','observerede timer')+'</small>':hourCount?'<small>'+hourCount+' '+txt('verified hourly closes · daily close not verified','verificerede timesluk · dagsluk endnu ikke verificeret')+'</small>':'');
    }
    readout(picked);
    host.querySelectorAll('[data-fw-day]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.fwDay);readout(m.days[selected]);});
    host.querySelectorAll('[data-fw-asset]').forEach(b=>b.onclick=()=>{asset=b.dataset.fwAsset;mount(host,data);});
    if(!lib){host.querySelector('.fw-canvas').innerHTML='<p>'+txt('Chart could not load. Exact values remain available below.','Grafen kunne ikke indlæses. Præcise værdier er stadig tilgængelige nedenfor.')+'</p>';return;}
    const canvas=host.querySelector('.fw-canvas');
    const values=[...m.rows.flatMap(r=>[r.forecast_low,r.forecast_high]),...m.daily.flatMap(p=>[p.low,p.high]),...m.hourly.flatMap(p=>[p.value]),...m.days.filter(d=>d.actual).flatMap(d=>[d.actual.low,d.actual.high])];
    const min=Math.min(...values),max=Math.max(...values),padding=(max-min)*.10;
    const chart=lib.createChart(canvas,{autoSize:true,layout:{background:{type:lib.ColorType.Solid,color:'#0a1729'},textColor:'#91a2b9',fontFamily:'-apple-system,BlinkMacSystemFont,system-ui,sans-serif',fontSize:11,attributionLogo:true},grid:{vertLines:{color:'rgba(147,166,190,.055)'},horzLines:{color:'rgba(147,166,190,.09)'}},rightPriceScale:{borderColor:'#243247',minimumWidth:72,scaleMargins:{top:.13,bottom:.13}},timeScale:{borderColor:'#243247',timeVisible:false,rightOffset:.5,fixLeftEdge:true,fixRightEdge:true,lockVisibleTimeRangeOnResize:true,tickMarkFormatter:time=>new Date(typeof time==='number'?time*1000:time).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'short',timeZone:'UTC'})},crosshair:{mode:lib.CrosshairMode.Normal,vertLine:{color:'#6b809b',width:1,style:lib.LineStyle.Dashed,labelBackgroundColor:'#30435d'},horzLine:{color:'#6b809b',width:1,style:lib.LineStyle.Dashed,labelBackgroundColor:'#30435d'}},localization:{locale:window.CNI18n?.language==='da'?'da-DK':'en-US',priceFormatter:money,timeFormatter:t=>new Date(t*1000).toLocaleDateString(window.CNI18n?.language==='da'?'da-DK':'en-GB',{weekday:'long',day:'numeric',month:'short',timeZone:'UTC'})},handleScroll:{mouseWheel:false,pressedMouseMove:true,horzTouchDrag:true,vertTouchDrag:false},handleScale:{mouseWheel:true,pinch:true,axisPressedMouseMove:{time:true,price:true}}});
    const opts={priceLineVisible:false,lastValueVisible:false,crosshairMarkerVisible:true,lineWidth:2,autoscaleInfoProvider:()=>({priceRange:{minValue:min-padding,maxValue:max+padding}})};
    const plan=linePlan(m);
    const baseline=chart.addSeries(lib.LineSeries,{...opts,color:BLUE,lineType:lib.LineType.Simple,lineStyle:lib.LineStyle.Dashed,lineWidth:2});baseline.setData(plan.forecast);
    const scaleAnchor=chart.addSeries(lib.LineSeries,{...opts,color:'transparent',lineVisible:false,crosshairMarkerVisible:false});scaleAnchor.setData([...m.days.map(d=>({time:d.time,value:d.forecast?.high??d.range.forecast_high})),{time:m.end/1000,value:m.days[6].forecast?.high??m.days[6].range.forecast_high}]);
    // One original-source overlay in BOTH modes: exact 7d daily low/high envelope
    // plus observed high/low whiskers, or the three genuine legacy intervals.
    // Visual hierarchy remains just two primary closing-price strokes.
    scaleAnchor.attachPrimitive(new EvidenceOverlay(m,scaleAnchor));
    // Separate observed runs rather than trusting a line to bridge missing evidence.
    plan.actualRuns.forEach((points,i)=>{const latest=i===plan.actualRuns.length-1;const series=chart.addSeries(lib.LineSeries,{...opts,color:GREEN,lineStyle:lib.LineStyle.Solid,lineWidth:4,pointMarkersVisible:true,pointMarkersRadius:3,lastValueVisible:latest,priceLineVisible:latest,priceLineColor:'rgba(39,197,154,.30)',priceLineStyle:lib.LineStyle.Dashed});series.setData(points);});
    chart.timeScale().fitContent();
    const select=d=>{selected=d.index;readout(d);};
    chart.subscribeCrosshairMove(p=>{if(p.time===undefined)return;const d=m.days.find(d=>p.time>d.time&&p.time<=d.closeTime)||m.days.find(d=>p.time===d.time&&d.index===0);if(d)select(d);});
    chart.subscribeClick(p=>{if(p.time===undefined)return;const d=m.days.find(d=>p.time>d.time&&p.time<=d.closeTime)||m.days.find(d=>p.time===d.time&&d.index===0);if(d)select(d);});
    host.querySelectorAll('[data-fw-day]').forEach(b=>b.onclick=()=>select(m.days[Number(b.dataset.fwDay)]));
    host.querySelectorAll('[data-fw-asset]').forEach(b=>b.onclick=()=>{asset=b.dataset.fwAsset;mount(host,data);});
    host.querySelector('.fw-reset').onclick=()=>chart.timeScale().fitContent();
    instance={chart,host,data};
  }
  window.CNWeekChart={mount,model,linePlan,graphDescription};
  document.addEventListener('cn-language-change',()=>{if(instance?.host.isConnected)mount(instance.host,instance.data);});
})();
