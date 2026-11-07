import { ASSETS, MONDAY, buildWeek, expectedDaily, forecastFingerprint } from './full-week-fixture.mjs';

const DESIGNS={
  nordic:{index:"01 / 03",label:"NORDIC EDITORIAL",title:"Ugens retning.<br><em>Helt klart.</em>",
    description:"En fuldstændig lys og rolig præsentation. Prognosen er fokus, dokumentationen er til stede uden at være en sort dashboard-boks."},
  atelier:{index:"02 / 03",label:"ATELIER",title:"En uge.<br><em>Syv forventninger.</em>",
    description:"En mere varm, editorial grafoplevelse. Et stort præcist prisdiagram på en papirlys flade, efterfulgt af elegante underliggende facts."},
  signal:{index:"03 / 03",label:"SIGNAL DESK",title:"Se mønstret.<br><em>Følg udfaldet.</em>",
    description:"Et lyst analyse-cockpit med fuldt prioriteret datahierarki. Kompakte facts til venstre, original TradingView-graf til højre."}
};
const query=new URLSearchParams(location.search);
let concept=DESIGNS[query.get("design")]?query.get("design"):"nordic";
let hours=Math.max(8,Math.min(168,Number(query.get("hours"))||168));
let asset="BTC";
let nordicFullDetailsOpen=false;
const $=id=>document.getElementById(id);
const fmt=n=>typeof n==="number"?n.toLocaleString("da-DK",{minimumFractionDigits:0,maximumFractionDigits:0}):"—";
const dayNames=["Mandag","Tirsdag","Onsdag","Torsdag","Fredag","Lørdag","Søndag"];
const base=Date.parse(MONDAY);
const nativeDateNow=Date.now.bind(Date);
const frozenFingerprint=forecastFingerprint();
const fixtureKeys=Object.fromEntries(["BTC","ETH"].map(k=>[k,JSON.stringify(expectedDaily(k))]));

function stageName(n){
 if(n===168)return "Søndag, hele ugen";
 if(n<=24)return "Mandag";
 if(n<=48)return "Tirsdag";
 if(n<=72)return "Onsdag";
 if(n<=96)return "Torsdag";
 if(n<=120)return "Fredag";
 if(n<=144)return "Lørdag";
 return "Søndag";
}
function sourceAt(hoursCount){
 const epoch=base+hoursCount*3600000;
 return new Date(epoch).toLocaleString("da-DK",{timeZone:"Europe/Copenhagen",weekday:"short",day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"})+" (DK)";
}
function updateDescription(){
 const d=DESIGNS[concept];
 document.body.dataset.concept=concept;
 $("concept-number").textContent="DESIGN "+d.index+" · "+d.label;
 $("concept-title").innerHTML=d.title;
 $("concept-description").textContent=d.description;
 $("footer-design").textContent="Design "+d.index+" · "+d.label;
 const fold=$("daily-values-fold");
 if(fold)fold.open=concept==="nordic"?nordicFullDetailsOpen:true;
 const title=$("daily-section-title");
 if(title)title.textContent=concept==="nordic"?
   "Syv prisfelter, direkte på grafen":"Syv frosne prognosedage";
 $("sunday-close").textContent=fmt(ASSETS[asset].close[6]);
 for(const b of document.querySelectorAll("[data-concept-choice]")){
   b.setAttribute("aria-pressed",String(b.dataset.conceptChoice===concept));
 }
 const shell=document.querySelector(".chart-area");
 shell?.setAttribute("data-kompas-alternative",concept);
}
function updateNumbers(fixture){
 $("observed-hours").textContent=hours+" / 168";
 $("as-of-label").textContent=stageName(hours);
 $("observation-time").textContent=sourceAt(hours);
 $("slider-caption").textContent=hours+" af 168 timer, "+stageName(hours);
 $("time-slider").value=String(hours);
 document.querySelectorAll("[data-stage]").forEach(b=>b.setAttribute("aria-pressed",String(Number(b.dataset.stage)===hours)));
 const rows=fixture.data.public_live_precision.daily_observations[asset];
 $("daily-rows").innerHTML=expectedDaily(asset).map((p,i)=>{
   const observed=rows.find(x=>x.day===i+1);
   return '<tr><td><strong>'+dayNames[i]+'</strong><small>'+(9+i)+'. nov.</small></td>'+
     '<td><strong>'+fmt(p.expected_close)+'</strong></td><td>'+fmt(p.low)+'</td>'+
     '<td>'+fmt(p.high)+'</td><td class="actual-number">'+(observed?fmt(observed.close):"Afventer")+'</td></tr>';
 }).join("");
}
function ensureOriginalEngine(){
 if(!window.LightweightCharts||!window.CNWeekChart||typeof window.CNWeekChart.mount!=="function")
   throw Error("ORIGINAL_GITHUB_TRADINGVIEW_RUNTIME_MISSING");
}
function render(){
 const fixture=buildWeek({hours});
 // The native model validates that observations are not from its future.
 // Only on this ISOLATED QA route is the clock advanced with the scene.
 // This does not change the public site's clock or source.
 Date.now=()=>Date.parse(fixture.nowUtc);
 updateDescription();
 updateNumbers(fixture);
 const err=$("graph-error");
 try{
   ensureOriginalEngine();
   window.CNWeekChart.mount($("native-chart"),fixture.data);
   err.hidden=true;
   if(frozenFingerprint!==forecastFingerprint())throw Error("QA_FORECAST_MUTATED");
   for(const k of ["BTC","ETH"])if(JSON.stringify(expectedDaily(k))!==fixtureKeys[k])throw Error("QA_FORECAST_POINTS_CHANGED");
 }catch(e){
   err.hidden=false;
   err.textContent="Original GitHub-grafmotor kunne ikke vise testsiden: "+String(e.message||e);
   $("native-chart").textContent="";
 }
 const u=new URL(location.href);
 u.searchParams.set("design",concept);u.searchParams.set("hours",String(hours));
 history.replaceState(null,"",u);
}
$("daily-values-fold")?.addEventListener("toggle",e=>{
 if(concept==="nordic")nordicFullDetailsOpen=e.currentTarget.open;
});
document.querySelectorAll("[data-concept-choice]").forEach(b=>b.addEventListener("click",()=>{
 concept=b.dataset.conceptChoice;render();
}));
document.querySelectorAll("[data-stage]").forEach(b=>b.addEventListener("click",()=>{
 hours=Number(b.dataset.stage);render();
}));
$("time-slider").addEventListener("input",e=>{
 hours=Number(e.target.value);render();
});
$("native-chart").addEventListener("click",e=>{
 const b=e.target.closest?.("[data-fw-asset]");
 if(!b)return;
 asset=b.dataset.fwAsset==="ETH"?"ETH":"BTC";
 const fixture=buildWeek({hours});
 updateDescription();
 updateNumbers(fixture);
});
window.addEventListener("pagehide",()=>{Date.now=nativeDateNow;},{once:true});
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render,{once:true});
else render();
