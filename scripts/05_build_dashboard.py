"""Build the final self-contained outputs/dashboard.html from the raw CSV."""
import json
import pandas as pd

df = pd.read_csv("data/raw/Sample - Superstore.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")

records = []
for _, r in df.iterrows():
    records.append({
        "date": r["Order Date"].strftime("%Y-%m-%d"),
        "region": r["Region"],
        "state": r["State"],
        "category": r["Category"],
        "subcategory": r["Sub-Category"],
        "segment": r["Segment"],
        "sales": round(float(r["Sales"]), 2),
        "quantity": int(r["Quantity"]),
        "discount": float(r["Discount"]),
        "profit": round(float(r["Profit"]), 2),
    })

data_json = json.dumps(records, separators=(",", ":"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Superstore Business Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1" integrity="sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ" crossorigin="anonymous"></script>
<style>
:root {
  --bg-primary:#f8f9fa; --bg-card:#ffffff; --bg-header:#1a1a2e;
  --text-primary:#212529; --text-secondary:#6c757d; --text-on-dark:#ffffff;
  --blue:#2a78d6; --orange:#eb6834; --aqua:#1baf7a; --red:#e34948;
  --positive:#0ca30c; --negative:#d03b3b;
  --gap:16px; --radius:8px;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:var(--bg-primary); color:var(--text-primary); line-height:1.5; }
.dashboard-container { max-width:1400px; margin:0 auto; padding:var(--gap); }
.dashboard-header { background:var(--bg-header); color:var(--text-on-dark); padding:20px 24px; border-radius:var(--radius); margin-bottom:var(--gap); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }
.dashboard-header h1 { font-size:20px; font-weight:600; }
.dashboard-header p { font-size:12px; color:rgba(255,255,255,0.65); margin-top:2px; }
.filters { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
.filter-group { display:flex; flex-direction:column; gap:3px; }
.filter-group label { font-size:11px; color:rgba(255,255,255,0.7); text-transform:uppercase; letter-spacing:0.5px; }
.filter-group select { padding:6px 10px; border:1px solid rgba(255,255,255,0.25); border-radius:4px; background:rgba(255,255,255,0.1); color:var(--text-on-dark); font-size:13px; }
.filter-group select option { background:var(--bg-header); color:var(--text-on-dark); }
.kpi-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:var(--gap); margin-bottom:var(--gap); }
.kpi-card { background:var(--bg-card); border-radius:var(--radius); padding:18px 22px; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.kpi-label { font-size:12px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px; }
.kpi-value { font-size:26px; font-weight:700; }
.kpi-value.negative { color:var(--negative); }
.chart-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(440px,1fr)); gap:var(--gap); margin-bottom:var(--gap); }
.chart-container { background:var(--bg-card); border-radius:var(--radius); padding:18px 22px; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.chart-container h3 { font-size:14px; font-weight:600; margin-bottom:14px; }
.chart-container canvas { max-height:320px; }
.insights { background:var(--bg-card); border-radius:var(--radius); padding:20px 24px; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:var(--gap); }
.insights h3 { font-size:14px; margin-bottom:10px; }
.insights ul { padding-left:20px; font-size:13.5px; color:var(--text-primary); }
.insights li { margin-bottom:8px; }
.insights .tag { font-size:11px; color:var(--text-secondary); margin-top:10px; }
.heatmap-table { width:100%; border-collapse:collapse; font-size:13px; text-align:center; }
.heatmap-table th { padding:8px; font-size:12px; color:var(--text-secondary); text-transform:uppercase; }
.heatmap-table td { padding:12px; font-weight:600; border:2px solid var(--bg-primary); }
.table-section { background:var(--bg-card); border-radius:var(--radius); padding:20px 24px; box-shadow:0 1px 3px rgba(0,0,0,0.08); overflow-x:auto; }
.data-table { width:100%; border-collapse:collapse; font-size:13px; }
.data-table thead th { text-align:left; padding:10px 12px; border-bottom:2px solid #dee2e6; color:var(--text-secondary); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:0.5px; white-space:nowrap; user-select:none; cursor:pointer; }
.data-table thead th:hover { color:var(--text-primary); background:#f8f9fa; }
.data-table tbody td { padding:9px 12px; border-bottom:1px solid #f0f0f0; }
.data-table tbody tr:hover { background:#f8f9fa; }
.negative-text { color:var(--negative); font-weight:600; }
@media (max-width:768px) {
  .dashboard-header { flex-direction:column; align-items:flex-start; }
  .kpi-row { grid-template-columns:repeat(2,1fr); }
  .chart-row { grid-template-columns:1fr; }
}
</style>
</head>
<body>
<div class="dashboard-container">

  <header class="dashboard-header">
    <div>
      <h1>Superstore Business Dashboard</h1>
      <p>9,994 orders &middot; Jan 2014 &ndash; Dec 2017</p>
    </div>
    <div class="filters">
      <div class="filter-group"><label>Region</label><select id="f-region" onchange="dash.applyFilters()"><option value="all">All Regions</option></select></div>
      <div class="filter-group"><label>Category</label><select id="f-category" onchange="dash.applyFilters()"><option value="all">All Categories</option></select></div>
      <div class="filter-group"><label>Segment</label><select id="f-segment" onchange="dash.applyFilters()"><option value="all">All Segments</option></select></div>
    </div>
  </header>

  <section class="kpi-row">
    <div class="kpi-card"><div class="kpi-label">Total Sales</div><div class="kpi-value" id="kpi-sales">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Total Profit</div><div class="kpi-value" id="kpi-profit">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Profit Margin</div><div class="kpi-value" id="kpi-margin">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Loss-Making Line Items</div><div class="kpi-value" id="kpi-loss">-</div></div>
  </section>

  <div class="insights">
    <h3>Key Findings &amp; Recommendations (full 4-year dataset)</h3>
    <ul>
      <li><strong>Discount ceiling varies by category</strong>: Furniture turns unprofitable above ~21-30% discount; Technology holds up to ~31-40%. A single company-wide discount cap doesn't fit the data &mdash; set it per category.</li>
      <li><strong>Tables, Bookcases and Supplies are structural losses</strong> ($-17.7k, $-3.5k, $-1.2k respectively) &mdash; not a clearance or demand problem, since order volume for these grew every year. Their pre-set discount tier is simply too deep for their margin structure.</li>
      <li><strong>Machines quietly underperforms</strong>: $189k in sales but only 1.8% margin &mdash; high volume, near break-even, easy to overlook next to outright losses.</li>
      <li><strong>Texas is the single biggest dollar loss</strong> (-$25.7k on $170k sales); Ohio has the worst percentage margin (-21.7%). Five states (TX, OH, IL, PA, NC) are net-negative despite real sales volume.</li>
      <li><strong>Best combination to grow</strong>: Office Supplies &times; Home Office (21% margin) and Technology &times; Corporate (18%) &mdash; Furniture is weak across every segment (2-3%).</li>
    </ul>
    <div class="tag">These findings reference the full dataset; the charts above respond to the filters.</div>
  </div>

  <section class="chart-row">
    <div class="chart-container"><h3>Monthly Sales &amp; Profit</h3><canvas id="chart-trend"></canvas></div>
    <div class="chart-container"><h3>Profit by Sub-Category (red = net loss)</h3><canvas id="chart-subcat"></canvas></div>
  </section>

  <section class="chart-row">
    <div class="chart-container"><h3>Discount vs. Profit, by Category</h3><canvas id="chart-scatter"></canvas></div>
    <div class="chart-container"><h3>Profit Margin by State (worst &amp; best 8)</h3><canvas id="chart-state"></canvas></div>
  </section>

  <div class="insights">
    <h3>Profit Margin: Category &times; Segment</h3>
    <table class="heatmap-table" id="heatmap"></table>
  </div>

  <div class="table-section">
    <h3 style="margin-bottom:12px;font-size:14px;">Sub-Category Detail (click a header to sort)</h3>
    <div id="detail-table"></div>
  </div>

</div>

<script id="raw-data" type="application/json">__DATA_JSON__</script>
<script>
const RAW = JSON.parse(document.getElementById('raw-data').textContent);
const BLUE="#2a78d6", ORANGE="#eb6834", AQUA="#1baf7a", RED="#e34948", MUTED="#898781";
const CAT_COLORS = {"Furniture":BLUE, "Office Supplies":ORANGE, "Technology":AQUA};

function fmtCurrency(v){
  const sign = v < 0 ? "-" : "";
  const av = Math.abs(v);
  if (av >= 1e6) return sign + "$" + (av/1e6).toFixed(1) + "M";
  if (av >= 1e3) return sign + "$" + (av/1e3).toFixed(1) + "K";
  return sign + "$" + av.toFixed(0);
}
function fmtPct(v){ return (v*100).toFixed(1) + "%"; }

function populateSelect(id, field){
  const sel = document.getElementById(id);
  const values = [...new Set(RAW.map(d => d[field]))].sort();
  values.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v; opt.textContent = v;
    sel.appendChild(opt);
  });
}

class Dashboard {
  constructor(data){
    this.raw = data;
    this.charts = {};
    this.init();
  }
  init(){
    populateSelect('f-region','region');
    populateSelect('f-category','category');
    populateSelect('f-segment','segment');
    this.applyFilters();
  }
  getFilterValue(id){
    const v = document.getElementById(id).value;
    return v === 'all' ? null : v;
  }
  applyFilters(){
    const region = this.getFilterValue('f-region');
    const category = this.getFilterValue('f-category');
    const segment = this.getFilterValue('f-segment');
    this.filtered = this.raw.filter(r =>
      (!region || r.region === region) &&
      (!category || r.category === category) &&
      (!segment || r.segment === segment)
    );
    this.renderKPIs();
    this.renderTrend();
    this.renderSubcat();
    this.renderScatter();
    this.renderState();
    this.renderHeatmap();
    this.renderDetailTable();
  }
  renderKPIs(){
    const d = this.filtered;
    const sales = d.reduce((s,r)=>s+r.sales,0);
    const profit = d.reduce((s,r)=>s+r.profit,0);
    const margin = sales ? profit/sales : 0;
    const lossRate = d.length ? d.filter(r=>r.profit<0).length / d.length : 0;
    document.getElementById('kpi-sales').textContent = fmtCurrency(sales);
    const pEl = document.getElementById('kpi-profit');
    pEl.textContent = fmtCurrency(profit);
    pEl.className = 'kpi-value' + (profit < 0 ? ' negative' : '');
    const mEl = document.getElementById('kpi-margin');
    mEl.textContent = fmtPct(margin);
    mEl.className = 'kpi-value' + (margin < 0 ? ' negative' : '');
    document.getElementById('kpi-loss').textContent = fmtPct(lossRate);
  }
  groupSum(data, keyFn, valFn){
    const m = new Map();
    data.forEach(r => { const k = keyFn(r); m.set(k, (m.get(k)||0) + valFn(r)); });
    return m;
  }
  renderTrend(){
    const months = new Map();
    this.filtered.forEach(r => {
      const month = r.date.slice(0,7);
      if (!months.has(month)) months.set(month, {sales:0, profit:0});
      const m = months.get(month);
      m.sales += r.sales; m.profit += r.profit;
    });
    const labels = [...months.keys()].sort();
    const sales = labels.map(l => months.get(l).sales);
    const profit = labels.map(l => months.get(l).profit);
    if (this.charts.trend) this.charts.trend.destroy();
    this.charts.trend = new Chart(document.getElementById('chart-trend'), {
      type:'line',
      data:{ labels, datasets:[
        {label:'Sales', data:sales, borderColor:BLUE, backgroundColor:BLUE+'20', borderWidth:2, tension:0.25, pointRadius:0},
        {label:'Profit', data:profit, borderColor:ORANGE, backgroundColor:ORANGE+'20', borderWidth:2, tension:0.25, pointRadius:0},
      ]},
      options:{ responsive:true, maintainAspectRatio:false,
        plugins:{ legend:{position:'top', labels:{usePointStyle:true}},
          tooltip:{ callbacks:{ label:c => c.dataset.label+': '+fmtCurrency(c.parsed.y) } } },
        scales:{ y:{ ticks:{ callback:v=>fmtCurrency(v) } } } }
    });
  }
  renderSubcat(){
    const sales = this.groupSum(this.filtered, r=>r.subcategory, r=>r.sales);
    const profit = this.groupSum(this.filtered, r=>r.subcategory, r=>r.profit);
    const labels = [...profit.keys()].sort((a,b) => profit.get(a) - profit.get(b));
    const values = labels.map(l => profit.get(l));
    const colors = values.map(v => v < 0 ? RED : BLUE);
    if (this.charts.subcat) this.charts.subcat.destroy();
    this.charts.subcat = new Chart(document.getElementById('chart-subcat'), {
      type:'bar',
      data:{ labels, datasets:[{ data:values, backgroundColor:colors, borderRadius:3 }] },
      options:{ responsive:true, maintainAspectRatio:false, indexAxis:'y',
        plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:c=>fmtCurrency(c.parsed.x) } } },
        scales:{ x:{ ticks:{ callback:v=>fmtCurrency(v) } } } }
    });
  }
  renderScatter(){
    const cats = [...new Set(this.filtered.map(r=>r.category))];
    const datasets = cats.map(cat => ({
      label:cat,
      data:this.filtered.filter(r=>r.category===cat).map(r=>({x:r.discount, y:r.profit})),
      backgroundColor:(CAT_COLORS[cat]||MUTED)+'99',
      pointRadius:3,
    }));
    if (this.charts.scatter) this.charts.scatter.destroy();
    this.charts.scatter = new Chart(document.getElementById('chart-scatter'), {
      type:'scatter',
      data:{ datasets },
      options:{ responsive:true, maintainAspectRatio:false,
        plugins:{ legend:{position:'top', labels:{usePointStyle:true}},
          tooltip:{ callbacks:{ label:c => c.dataset.label+': discount '+fmtPct(c.parsed.x)+', profit '+fmtCurrency(c.parsed.y) } } },
        scales:{ x:{ title:{display:true, text:'Discount'}, ticks:{callback:v=>fmtPct(v)} },
                 y:{ title:{display:true, text:'Profit'}, ticks:{callback:v=>fmtCurrency(v)} } } }
    });
  }
  renderState(){
    const sales = this.groupSum(this.filtered, r=>r.state, r=>r.sales);
    const profit = this.groupSum(this.filtered, r=>r.state, r=>r.profit);
    const margins = [...sales.keys()].map(s => [s, sales.get(s) ? profit.get(s)/sales.get(s) : 0]);
    margins.sort((a,b) => a[1]-b[1]);
    const picked = [...margins.slice(0,8), ...margins.slice(-8)];
    const labels = picked.map(p=>p[0]);
    const values = picked.map(p=>p[1]);
    const colors = values.map(v => v < 0 ? RED : BLUE);
    if (this.charts.state) this.charts.state.destroy();
    this.charts.state = new Chart(document.getElementById('chart-state'), {
      type:'bar',
      data:{ labels, datasets:[{ data:values, backgroundColor:colors, borderRadius:3 }] },
      options:{ responsive:true, maintainAspectRatio:false, indexAxis:'y',
        plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:c=>fmtPct(c.parsed.x) } } },
        scales:{ x:{ ticks:{ callback:v=>fmtPct(v) } } } }
    });
  }
  renderHeatmap(){
    const cats = [...new Set(this.filtered.map(r=>r.category))].sort();
    const segs = [...new Set(this.filtered.map(r=>r.segment))].sort();
    let html = '<tr><th></th>' + segs.map(s=>`<th>${s}</th>`).join('') + '</tr>';
    cats.forEach(cat => {
      html += `<tr><th style="text-align:left">${cat}</th>`;
      segs.forEach(seg => {
        const rows = this.filtered.filter(r=>r.category===cat && r.segment===seg);
        const sales = rows.reduce((s,r)=>s+r.sales,0);
        const profit = rows.reduce((s,r)=>s+r.profit,0);
        const margin = sales ? profit/sales : 0;
        const bg = margin < 0 ? '#f3c9c7' : `rgba(42,120,214,${Math.min(0.15 + margin*3, 0.9)})`;
        const textColor = margin > 0.12 ? '#fff' : '#0b0b0b';
        html += `<td style="background:${bg};color:${textColor}">${fmtPct(margin)}</td>`;
      });
      html += '</tr>';
    });
    document.getElementById('heatmap').innerHTML = html;
  }
  renderDetailTable(){
    const sales = this.groupSum(this.filtered, r=>r.subcategory, r=>r.sales);
    const profit = this.groupSum(this.filtered, r=>r.subcategory, r=>r.profit);
    const discSum = this.groupSum(this.filtered, r=>r.subcategory, r=>r.discount);
    const counts = this.groupSum(this.filtered, r=>r.subcategory, r=>1);
    let rows = [...sales.keys()].map(k => ({
      subcategory:k, sales:sales.get(k), profit:profit.get(k),
      margin: sales.get(k) ? profit.get(k)/sales.get(k) : 0,
      avgDiscount: discSum.get(k)/counts.get(k),
    }));
    let sortCol = 'profit', sortDir = 'asc';
    const cols = [
      {key:'subcategory', label:'Sub-Category', fmt:v=>v},
      {key:'sales', label:'Sales', fmt:fmtCurrency},
      {key:'profit', label:'Profit', fmt:v=>`<span class="${v<0?'negative-text':''}">${fmtCurrency(v)}</span>`},
      {key:'margin', label:'Margin', fmt:v=>`<span class="${v<0?'negative-text':''}">${fmtPct(v)}</span>`},
      {key:'avgDiscount', label:'Avg Discount', fmt:fmtPct},
    ];
    const container = document.getElementById('detail-table');
    const render = () => {
      const sorted = [...rows].sort((a,b) => {
        const cmp = a[sortCol] < b[sortCol] ? -1 : a[sortCol] > b[sortCol] ? 1 : 0;
        return sortDir === 'asc' ? cmp : -cmp;
      });
      let html = '<table class="data-table"><thead><tr>';
      cols.forEach(c => {
        const arrow = sortCol===c.key ? (sortDir==='asc'?' ▲':' ▼') : '';
        html += `<th data-key="${c.key}">${c.label}${arrow}</th>`;
      });
      html += '</tr></thead><tbody>';
      sorted.forEach(r => {
        html += '<tr>' + cols.map(c => `<td>${c.fmt(r[c.key])}</td>`).join('') + '</tr>';
      });
      html += '</tbody></table>';
      container.innerHTML = html;
      container.querySelectorAll('th').forEach(th => {
        th.onclick = () => {
          const key = th.dataset.key;
          if (sortCol === key) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
          else { sortCol = key; sortDir = 'asc'; }
          render();
        };
      });
    };
    render();
  }
}
const dash = new Dashboard(RAW);
</script>
</body>
</html>
"""

html = html.replace("__DATA_JSON__", data_json)

with open("outputs/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote outputs/dashboard.html with {len(records)} embedded records")
