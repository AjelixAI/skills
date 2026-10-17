# Chart Recipes

Copy-paste ECharts / Chart.js snippets. Each is a complete, working `setOption`
body — paste it into the blueprint shell and swap the data.

Why ECharts by default: consistent styling, good defaults, one library covers
every chart below. Chart.js equivalents are given where it is meaningfully simpler.

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>
```

Every chart needs a container with an **explicit height**, plus a resize handler:

```html
<div id="chart" style="width:100%;height:320px;"></div>
<script>
  var chart = echarts.init(document.getElementById('chart'));
  chart.setOption({ /* …a recipe below… */ });
  window.addEventListener('resize', function () { chart.resize(); });
</script>
```

Shared helpers used throughout:

```js
var PALETTE = ['#6d28d9', '#0ea5e9', '#059669', '#d97706', '#dc2626', '#7c3aed'];
var eur = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
var pct = new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 1 });

// Reusable axis chrome matching the Ajelix palette.
function axis() {
  return {
    axisLine: { lineStyle: { color: '#e4e4e7' } },
    axisLabel: { color: '#6b6b75', fontSize: 11 }
  };
}
function tip(formatter) {
  return {
    trigger: 'axis',
    valueFormatter: formatter,
    borderColor: '#e4e4e7',
    textStyle: { color: '#18181b', fontSize: 12 }
  };
}
var GRID = { left: 8, right: 16, top: 24, bottom: 8, containLabel: true };
```

---

## Line — trend over time

```js
chart.setOption({
  grid: GRID,
  tooltip: tip(function (v) { return eur.format(v); }),
  xAxis: Object.assign({ type: 'category', data: months, boundaryGap: false }, axis()),
  yAxis: Object.assign({ type: 'value', splitLine: { lineStyle: { color: '#f0f0f2' } } }, axis()),
  series: [{
    type: 'line', smooth: true, symbolSize: 6, data: values,
    lineStyle: { width: 2, color: PALETTE[0] },
    itemStyle: { color: PALETTE[0] },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(109,40,217,.18)' },
        { offset: 1, color: 'rgba(109,40,217,0)' }
      ])
    }
  }]
});
```

**Multi-series** — add more objects to `series` and give each its own colour from
`PALETTE`. Always add a `legend` when there is more than one series:

```js
legend: { bottom: 0, icon: 'roundRect', itemWidth: 10, itemHeight: 10,
          textStyle: { color: '#6b6b75', fontSize: 11 } },
```

**Comparison (this period vs last)** — same chart, second series dashed:

```js
series: [
  { type: 'line', smooth: true, name: 'This year', data: current,
    lineStyle: { width: 2, color: PALETTE[0] }, itemStyle: { color: PALETTE[0] } },
  { type: 'line', smooth: true, name: 'Last year', data: previous,
    lineStyle: { width: 2, type: 'dashed', color: '#9ca3af' },
    itemStyle: { color: '#9ca3af' } }
]
```

---

## Bar — comparison across categories

```js
chart.setOption({
  grid: GRID,
  tooltip: tip(function (v) { return eur.format(v); }),
  xAxis: Object.assign({ type: 'category', data: categories }, axis()),
  yAxis: Object.assign({ type: 'value', splitLine: { lineStyle: { color: '#f0f0f2' } } }, axis()),
  series: [{
    type: 'bar', data: values, barMaxWidth: 44,
    itemStyle: { color: PALETTE[0], borderRadius: [6, 6, 0, 0] }
  }]
});
```

**Horizontal** (better for long category names) — swap the axes and round the other end:

```js
xAxis: Object.assign({ type: 'value', splitLine: { lineStyle: { color: '#f0f0f2' } } }, axis()),
yAxis: Object.assign({ type: 'category', data: categories, inverse: true }, axis()),
series: [{ type: 'bar', data: values, barMaxWidth: 24,
           itemStyle: { color: PALETTE[0], borderRadius: [0, 6, 6, 0] } }]
```

**Grouped / stacked** — one series per group; add `stack: 'total'` to stack:

```js
series: [
  { type: 'bar', name: 'New', data: newValues, itemStyle: { color: PALETTE[0] } },
  { type: 'bar', name: 'Returning', data: retValues, itemStyle: { color: PALETTE[1] } }
]
```

**Diverging (positive/negative)** — colour per point:

```js
series: [{
  type: 'bar', barMaxWidth: 36, data: values,
  itemStyle: {
    borderRadius: 4,
    color: function (p) { return p.value >= 0 ? '#059669' : '#dc2626'; }
  }
}]
```

---

## Pie / donut — composition

```js
chart.setOption({
  tooltip: { trigger: 'item', valueFormatter: function (v) { return eur.format(v); },
             borderColor: '#e4e4e7', textStyle: { color: '#18181b', fontSize: 12 } },
  legend: { bottom: 0, icon: 'roundRect', itemWidth: 10, itemHeight: 10,
            textStyle: { color: '#6b6b75', fontSize: 11 } },
  color: PALETTE,
  series: [{
    type: 'pie',
    radius: ['50%', '72%'],           // inner radius > 0 makes it a donut
    center: ['50%', '44%'],
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
    label: { show: false },           // labels off; the legend + tooltip carry it
    emphasis: { label: { show: true, fontSize: 13, fontWeight: 600, formatter: '{b}\n{d}%' } },
    data: rows.map(function (r) { return { name: r.label, value: r.value }; })
  }]
});
```

Donut > pie: the hole gives the eye an anchor and reads better at small sizes.
Above ~6 slices, switch to a horizontal bar — pie slices become unreadable.

---

## Scatter — correlation

```js
chart.setOption({
  grid: GRID,
  tooltip: { trigger: 'item', borderColor: '#e4e4e7',
             textStyle: { color: '#18181b', fontSize: 12 } },
  xAxis: Object.assign({ type: 'value', name: 'Spend', nameTextStyle: { color: '#9ca3af' },
                         splitLine: { lineStyle: { color: '#f0f0f2' } } }, axis()),
  yAxis: Object.assign({ type: 'value', name: 'Revenue', nameTextStyle: { color: '#9ca3af' },
                         splitLine: { lineStyle: { color: '#f0f0f2' } } }, axis()),
  series: [{
    type: 'scatter', symbolSize: 10,
    itemStyle: { color: 'rgba(109,40,217,.55)', borderColor: '#6d28d9' },
    data: points      // [[x, y], [x, y], …]
  }]
});
```

---

## Gauge — a single KPI against a target

```js
chart.setOption({
  series: [{
    type: 'gauge',
    startAngle: 200, endAngle: -20,
    min: 0, max: 100,
    progress: { show: true, width: 14, itemStyle: { color: PALETTE[0] } },
    axisLine: { lineStyle: { width: 14, color: [[1, '#f0f0f2']] } },
    axisTick: { show: false },
    splitLine: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    detail: {
      valueAnimation: true,
      offsetCenter: [0, 0],
      fontSize: 30, fontWeight: 700, color: '#18181b',
      formatter: '{value}%'
    },
    data: [{ value: 68 }]
  }]
});
```

---

## Sparkline — inline trend, no axes

```js
chart.setOption({
  grid: { left: 0, right: 0, top: 4, bottom: 0 },
  xAxis: { type: 'category', show: false, data: months, boundaryGap: false },
  yAxis: { type: 'value', show: false, scale: true },
  series: [{ type: 'line', smooth: true, symbol: 'none', data: values,
             lineStyle: { width: 2, color: PALETTE[0] },
             areaStyle: { color: 'rgba(109,40,217,.10)' } }],
  tooltip: { show: false }
});
```

Container height 40–60px. Put the current value next to it as plain text — a
sparkline shows *shape*, not magnitude.

---

## Heatmap — two dimensions

```js
chart.setOption({
  tooltip: { position: 'top', borderColor: '#e4e4e7',
             textStyle: { color: '#18181b', fontSize: 12 } },
  grid: { left: 8, right: 8, top: 8, bottom: 40, containLabel: true },
  xAxis: Object.assign({ type: 'category', data: days, splitArea: { show: true } }, axis()),
  yAxis: Object.assign({ type: 'category', data: hours, splitArea: { show: true } }, axis()),
  visualMap: {
    min: 0, max: 100, calculable: true, orient: 'horizontal',
    left: 'center', bottom: 0, itemHeight: 80,
    textStyle: { color: '#6b6b75', fontSize: 11 },
    inRange: { color: ['#f0f0f2', '#c4b5fd', '#6d28d9'] }
  },
  series: [{
    type: 'heatmap', data: cells,          // [[xIndex, yIndex, value], …]
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
    emphasis: { itemStyle: { shadowBlur: 6, shadowColor: 'rgba(0,0,0,.2)' } }
  }]
});
```

---

## Funnel — stage conversion

```js
chart.setOption({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)',
             borderColor: '#e4e4e7', textStyle: { color: '#18181b', fontSize: 12 } },
  color: PALETTE,
  series: [{
    type: 'funnel', left: '8%', width: '84%', top: 8, bottom: 8,
    minSize: '24%', gap: 4, sort: 'descending',
    label: { position: 'inside', color: '#fff', fontSize: 12, fontWeight: 600 },
    itemStyle: { borderColor: '#fff', borderWidth: 1 },
    data: stages                            // [{ name, value }, …]
  }]
});
```

---

## Chart.js equivalents (simpler, smaller)

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
```

```js
new Chart(document.getElementById('c'), {
  type: 'bar',                              // or 'line' | 'doughnut' | 'radar'
  data: {
    labels: categories,
    datasets: [{ label: 'Revenue', data: values, backgroundColor: '#6d28d9', borderRadius: 6 }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,             // required: canvas fills its parent
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#f0f0f2' }, ticks: { color: '#6b6b75' } },
      x: { grid: { display: false }, ticks: { color: '#6b6b75' } }
    }
  }
});
```

With `maintainAspectRatio: false` the canvas **must** sit in a fixed-height parent:

```html
<div style="height:320px"><canvas id="c"></canvas></div>
```

---

## Choosing a chart

| The data shows… | Use |
|---|---|
| Change over time | Line (area if a single series) |
| Comparison across categories | Bar; horizontal bar if names are long |
| Composition of a whole | Donut (≤ 6 slices), stacked bar otherwise |
| Relationship between two measures | Scatter |
| One value against a target | Gauge, or a KPI card + progress bar |
| Shape of a trend, no axes | Sparkline inside a KPI card |
| Intensity across two dimensions | Heatmap |
| Drop-off through stages | Funnel |

## Rules that apply to every chart

- **Container height is mandatory.** A chart in a zero-height or `auto` parent
  renders blank. This is the single most common chart bug.
- **Resize handler is mandatory** (or a `ResizeObserver`). The preview panel is
  resizable; a chart that never resizes is visibly broken.
- **Format numbers.** `Intl.NumberFormat` — never raw floats. `€284,900`, not
  `284900.00000001`.
- **No chartjunk.** Drop gridlines you don't need, never add 3D, never add a
  second y-axis to make two unrelated series "fit".
- **Colour is never the only signal.** Pair it with a label, an arrow, or a sign.
- **Fewer series beats more.** Past 5 series a chart is a table.
- **Sort meaningfully.** Alphabetical is rarely the point; descending by value
  usually is.
- **Annotate the one thing that matters** with `markLine` / `markPoint` rather
  than a paragraph under the chart.
