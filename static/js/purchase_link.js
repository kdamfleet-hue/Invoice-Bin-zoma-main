(function(){
  if (location.pathname.indexOf('/purchase') !== 0) return;
  function archive(){
    if (typeof collectPOData !== 'function') return null;
    const d = collectPOData();
    let list=[];
    try{list=JSON.parse(localStorage.getItem('poArchive')||'[]');}catch(e){list=[];}
    list = list.filter(x => String(x.serial) !== String(d.serial));
    list.unshift(d);
    localStorage.setItem('poArchive', JSON.stringify(list.slice(0,200)));
    try{
      fetch('/api/purchase_data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d),credentials:'same-origin'});
    }catch(e){}
    return d;
  }
  function routeTo(path){
    const d=archive();
    if(!d) return;
    location.href = path + '?po=' + encodeURIComponent(d.serial||'') + '&plate=' + encodeURIComponent(d.plate||'');
  }
  function restoreBySerial(s){
    let list=[];
    try{list=JSON.parse(localStorage.getItem('poArchive')||'[]');}catch(e){}
    const d=list.find(x=>String(x.serial)===String(s));
    if(d && typeof wsRestorePO==='function'){ wsRestorePO(d); }
    else if(d){
      const set=(id,v)=>{const el=document.getElementById(id); if(el && v!=null) el.value=v;};
      set('poSerial',d.serial); set('poDriver',d.driver); set('poPlate',d.plate);
      set('poCar',d.car); set('poDate',d.date); set('poNotes',d.notes);
    }
  }
  document.addEventListener('DOMContentLoaded', function(){
    const bar=document.createElement('div');
    bar.className='pdf-exclude';
    bar.style.cssText='display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:12px 0';
    bar.innerHTML='<button class="btn-neon" type="button" id="poSaveBtn">حفظ الطلب وربطه بالمخزون</button>'
      +'<button class="btn-neon" type="button" id="poTiresBtn">إرفاق الكفرات ← الإطارات</button>'
      +'<button class="btn-neon" type="button" id="poBattBtn">إرفاق البطاريات ← البطاريات</button>'
      +'<button class="btn-neon" type="button" id="poPartsBtn">إرفاق القطع ← قطع الغيار</button>'
      +'<a class="bz-chip" href="/purchase/list">قائمة الطلبات</a>';
    const area=document.getElementById('poFormArea');
    if(area) area.prepend(bar);
    else document.querySelector('.main-content')?.prepend(bar);
    const s=document.getElementById('poSaveBtn');
    if(s) s.onclick=function(){ archive(); location.href='/purchase/list'; };
    const t=document.getElementById('poTiresBtn'); if(t) t.onclick=function(){ routeTo('/inventory/tires'); };
    const b=document.getElementById('poBattBtn'); if(b) b.onclick=function(){ routeTo('/inventory/batteries'); };
    const p=document.getElementById('poPartsBtn'); if(p) p.onclick=function(){ routeTo('/spare_parts'); };
    const qs=new URLSearchParams(location.search).get('serial');
    if(qs) setTimeout(function(){ restoreBySerial(qs); }, 400);

    function linkTable(tableId, path, label){
      const th=document.querySelector('#'+tableId+' thead .excel-header');
      if(!th || th.querySelector('.po-link-tab')) return;
      const a=document.createElement('button');
      a.type='button'; a.className='btn-add-row pdf-exclude po-link-tab';
      a.textContent=label;
      a.style.marginRight='8px';
      a.onclick=function(){ routeTo(path); };
      th.appendChild(a);
    }
    linkTable('tiresTable','/inventory/tires','ربط بتبويب الإطارات');
    linkTable('batteriesTable','/inventory/batteries','ربط بتبويب البطاريات');
    linkTable('partsTable','/spare_parts','ربط بتبويب القطع');
  });
  const wrap = function(name){
    const orig = window[name];
    if (typeof orig !== 'function') return;
    window[name] = async function(){
      archive();
      return orig.apply(this, arguments);
    };
  };
  wrap('downloadPO');
  wrap('sharePO');
})();
