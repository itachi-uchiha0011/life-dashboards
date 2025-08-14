(function(){
  // Theme toggle
  const root = document.documentElement;
  const applyTheme = (t)=>document.documentElement.setAttribute('data-bs-theme', t);
  const saved = localStorage.getItem('theme') || 'light';
  applyTheme(saved);
  const toggleBtn = document.getElementById('theme-toggle');
  if (toggleBtn){
    toggleBtn.addEventListener('click', ()=>{
      const cur = document.documentElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
      applyTheme(cur); localStorage.setItem('theme', cur);
    });
  }

  // Quill init helper
  window.syncQuill = function(editorId, inputId){
    const el = document.getElementById(editorId);
    if (!el) return;
    const q = Quill.find(el) || new Quill(el, { theme: 'snow' });
    document.getElementById(inputId).value = el.querySelector('.ql-editor').innerHTML;
  };

  document.querySelectorAll('.quill-editor').forEach(el=>{
    if (!Quill.find(el)) new Quill(el, { theme: 'snow' });
  });

  // Heatmap using Chart.js Matrix
  const heatmapCanvas = document.getElementById('heatmap');
  if (heatmapCanvas){
    fetch('/api/journal/heatmap').then(r=>r.json()).then(data=>{
      const days = {};
      data.forEach(d=>{ days[d.date] = d.count; });
      const today = new Date();
      const start = new Date(today.getTime() - 365*24*60*60*1000);
      const values = [];
      for(let d=new Date(start); d<=today; d.setDate(d.getDate()+1)){
        const key = d.toISOString().slice(0,10);
        const week = getWeekNumber(d);
        const dow = d.getDay();
        values.push({x: week, y: dow, v: days[key] || 0, date: key});
      }
      const weeks = [...new Set(values.map(v=>v.x))];
      const chart = new Chart(heatmapCanvas, {
        type: 'matrix',
        data: {
          datasets: [{
            label: 'Journal Heatmap',
            data: values,
            width: ({chart}) => (chart.chartArea || {}).width / weeks.length - 2,
            height: ({chart}) => (chart.chartArea || {}).height / 7 - 2,
            backgroundColor: ctx => {
              const v = ctx.raw.v; const alpha = v ? Math.min(0.1 + v/5, 1) : 0.05; return `rgba(13,110,253,${alpha})`;
            },
            borderWidth: 1,
            borderColor: 'rgba(0,0,0,0.05)'
          }]
        },
        options: {
          maintainAspectRatio: false,
          scales: {
            x: { type: 'linear', ticks: { callback: ()=>'' } },
            y: { type: 'linear', ticks: { callback: v => ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][v] } }
          },
          plugins: { tooltip: { callbacks: { label: (ctx)=> `${ctx.raw.date}: ${ctx.raw.v}` } } },
          onClick: (evt) => {
            const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
            if (points.length){
              const raw = chart.data.datasets[points[0].datasetIndex].data[points[0].index];
              if (raw && raw.date){
                window.location.href = `/journal/day/${raw.date}`;
              }
            }
          }
        }
      });
    });
  }

  function getWeekNumber(d){
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const dayNum = date.getUTCDay() || 7;
    date.setUTCDate(date.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(),0,1));
    return Math.ceil((((date - yearStart) / 86400000) + 1)/7);
  }

  // Todos UI
  document.querySelectorAll('.add-todo').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const wrapper = btn.closest('.card-body');
      const input = wrapper.querySelector('input[type=text]');
      const kind = wrapper.getAttribute('data-kind');
      const label = input.value.trim(); if (!label) return;
      const csrf = document.querySelector('meta[name=csrf-token]')?.content || '';
      fetch('/api/todos', {method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken': csrf}, body: JSON.stringify({label, kind})})
        .then(()=> location.reload());
    });
  });
  document.querySelectorAll('.todo-toggle').forEach(chk=>{
    chk.addEventListener('change', ()=>{
      const csrf = document.querySelector('meta[name=csrf-token]')?.content || '';
      fetch(`/api/todos/${chk.dataset.id}/toggle`, {method:'POST', headers:{'X-CSRFToken': csrf}})
        .then(()=> location.reload());
    });
  });
})();