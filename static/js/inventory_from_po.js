(function(){
  const path = location.pathname;
  const po = new URLSearchParams(location.search).get('po');
  const plateQ = new URLSearchParams(location.search).get('plate');
  if(!po) return;
  let item=null;
  try{
    const list=JSON.parse(localStorage.getItem('poArchive')||'[]');
    item=list.find(x=>String(x.serial)===String(po));
  }catch(e){}
  if(!item) return;
  function banner(html){
    const d=document.createElement('div');
    d.className='glass-panel';
    d.style.cssText='padding:12px;margin:0 0 12px;border:1px solid rgba(201,164,90,.35)';
    d.innerHTML=html;
    const main=document.querySelector('.main-content')||document.body;
    main.insertBefore(d, main.firstChild);
  }
  const links = `<div style="margin-top:8px"><a class="bz-chip" href="/purchase/list">رجوع لقائمة المشتريات</a> <a class="bz-chip" href="/purchase?serial=${encodeURIComponent(po)}">فتح الطلب ${po}</a></div>`;
  const plate = item.plate || plateQ || '';
  if(path.indexOf('/inventory/tires')===0){
    banner(`<b>وارد من طلب شراء ${po}</b> — لوحة ${plate||'—'} · سائق ${item.driver||'—'}<br>عدد سجلات الكفرات: ${(item.tires||[]).length}${links}`);
    (item.tires||[]).forEach((t,i)=>{
      const serial = t.serial || t.serial_number || (`PO-${po}-T${i+1}`);
      fetch('/api/inventory/tires',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({
        serial_number: serial,
        vehicle_plate: plate,
        brand: t.brand || 'طلب شراء',
        size: t.size || '',
        install_date: t.date || '',
        status: 'جديد',
        notes: `طلب شراء ${po} — العدد ${t.count||1}`
      })}).catch(()=>{});
    });
  }
  if(path.indexOf('/inventory/batteries')===0){
    banner(`<b>وارد من طلب شراء ${po}</b> — لوحة ${plate||'—'} · سائق ${item.driver||'—'}<br>البطاريات: ${(item.batteries||[]).map(b=>b.desc||'بطارية').join('، ')||'لا صفوف'}${links}`);
    (item.batteries||[]).forEach((b,i)=>{
      const serial = b.serial || b.serial_number || (`PO-${po}-B${i+1}`);
      fetch('/api/inventory/batteries',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({
        serial_number: serial,
        vehicle_plate: plate,
        brand: b.desc || b.brand || 'طلب شراء',
        capacity: b.amp || b.capacity || b.size || '',
        install_date: b.date || '',
        status: 'نشط',
        notes: `طلب شراء ${po}`
      })}).catch(()=>{});
    });
  }
  if(path.indexOf('/spare_parts')===0){
    banner(`<b>وارد من طلب شراء ${po}</b> — لوحة ${plate||'—'} · سائق ${item.driver||'—'}<br>القطع: ${(item.parts||[]).map(p=>p.desc||'قطعة').join('، ')||'لا صفوف'}${links}`);
    (item.parts||[]).forEach((p,i)=>{
      fetch('/api/spare_parts',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({
        part_number: p.part_number || (`PO-${po}-P${i+1}`),
        name: p.desc || p.name || 'قطعة من طلب شراء',
        category: 'طلب شراء',
        quantity: p.qty || p.quantity || 1,
        unit_price: p.price || 0,
        supplier: 'PO '+po
      })}).catch(()=>{});
    });
  }
})();
