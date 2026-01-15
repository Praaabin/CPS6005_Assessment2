/**
 * D3.js Interactive Congestion Heatmap
 * 
 * Features:
 * - Switchable Metrics: Volume (Count) vs Speed (Avg Speed)
 * - Dynamic Color Scales
 * - Glassmorphism Tooltips
 * - Smooth Transitions
 */

const initHeat = setInterval(() => {
    const root = document.getElementById("d3-heatmap-root");
    if (root && window.d3) {
        clearInterval(initHeat);
        renderHeatmap(root);
    }
}, 300);

async function renderHeatmap(root) {
    root.innerHTML = "";

    // -- Controls --
    const controls = document.createElement("div");
    controls.style.cssText = `
        display: flex; gap: 12px; margin-bottom: 10px; justify-content: flex-end;
    `;

    // Toggle Logic
    let currentMetric = "count"; // count | avg_speed

    const createBtn = (id, label) => {
        const btn = document.createElement("button");
        btn.innerText = label;
        btn.style.cssText = `
            padding: 6px 16px; border-radius: 20px; border: 1px solid #cbd5e1;
            background: #fff; cursor: pointer; font-size: 13px; font-weight: 600;
            color: #475569; transition: all 0.2s;
        `;
        btn.onclick = () => {
            currentMetric = id;
            updateChart();
            updateButtons();
        };
        return btn;
    };

    const btnCount = createBtn("count", "📊 Traffic Volume");
    const btnSpeed = createBtn("avg_speed", "🚀 Avg Speed");

    function updateButtons() {
        [btnCount, btnSpeed].forEach(b => {
            b.style.background = "#fff"; b.style.color = "#475569"; b.style.borderColor = "#cbd5e1";
        });
        const active = currentMetric === "count" ? btnCount : btnSpeed;
        active.style.background = currentMetric === "count" ? "#f43f5e" : "#3b82f6";
        active.style.color = "#fff";
        active.style.borderColor = "transparent";
    }

    controls.appendChild(btnCount);
    controls.appendChild(btnSpeed);
    root.appendChild(controls);

    // -- Container --
    const container = document.createElement("div");
    container.style.position = "relative";
    root.appendChild(container);

    const url = "/assets/data/congestion_heatmap.json";
    let data;
    try {
        data = await d3.json(url);
    } catch (e) {
        container.innerHTML = `<div style="color:#b91c1c;font-weight:700;">❌ Could not load ${url}.</div>`;
        return;
    }

    if (!data || !data.length) {
        container.innerHTML = `<div style="color:#b91c1c;font-weight:700;">❌ No data found.</div>`;
        return;
    }

    // Process Data
    const hours = Array.from(new Set(data.map(d => +d.hour))).sort((a, b) => a - b);
    const levels = Array.from(new Set(data.map(d => d.Degree_of_congestion))).sort(); // Maybe custom sort?

    // Custom sort for levels if possible
    const levelOrder = ["Very smooth", "Smooth", "Mild congestion", "Heavy congestion", "Severe"];
    levels.sort((a, b) => {
        const ia = levelOrder.indexOf(a);
        const ib = levelOrder.indexOf(b);
        return (ia > -1 && ib > -1) ? ia - ib : 0;
    });

    // Dimensions
    const margin = { top: 20, right: 20, bottom: 50, left: 160 };
    const parentW = root.clientWidth || 900;
    const width = Math.min(1000, parentW) - margin.left - margin.right;
    const cellSize = 50;
    const height = levels.length * cellSize;

    const svg = d3.select(container).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleBand().domain(hours).range([0, width]).padding(0.08);
    const y = d3.scaleBand().domain(levels).range([height, 0]).padding(0.08);

    // Tooltip
    const tooltip = d3.select(container).append("div")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "rgba(255, 255, 255, 0.95)")
        .style("backdrop-filter", "blur(4px)")
        .style("padding", "10px 14px")
        .style("border-radius", "8px")
        .style("box-shadow", "0 10px 30px rgba(0,0,0,0.15)")
        .style("pointer-events", "none")
        .style("border", "1px solid rgba(0,0,0,0.05)")
        .style("font-size", "13px")
        .style("z-index", 100);

    // Axes
    g.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat(d => `${d}:00`))
        .select(".domain").remove();

    g.append("g")
        .call(d3.axisLeft(y).tickSize(0))
        .select(".domain").remove();

    g.selectAll(".tick text")
        .style("font-size", "12px")
        .style("font-weight", "600")
        .style("fill", "#64748b");

    // Labels
    g.append("text")
        .attr("x", width / 2)
        .attr("y", height + 40)
        .attr("text-anchor", "middle")
        .style("fill", "#94a3b8")
        .style("font-size", "11px")
        .style("font-weight", "bold")
        .text("HOUR OF DAY");

    // Cells Group
    const cellsG = g.append("g");

    function updateChart() {
        const isCount = currentMetric === "count";
        const maxVal = d3.max(data, d => +d[currentMetric]);

        // Color Scales
        // Count: White -> Orange -> Red
        const colorCount = d3.scaleSequential()
            .domain([0, maxVal])
            .interpolator(d3.interpolateYlOrRd);

        // Speed: Red (Slow) -> Green (Fast)
        // We invert logic: 0 speed is bad (Red), 60 speed is good (Green)
        const colorSpeed = d3.scaleSequential()
            .domain([0, maxVal]) // 0 to ~60
            .interpolator(d3.interpolateRdYlGn);

        const getColor = (val) => isCount ? colorCount(val) : colorSpeed(val);

        const rects = cellsG.selectAll("rect")
            .data(data, d => d.hour + "-" + d.Degree_of_congestion);

        // Enter
        rects.enter()
            .append("rect")
            .attr("x", d => x(+d.hour))
            .attr("y", d => y(d.Degree_of_congestion))
            .attr("width", x.bandwidth())
            .attr("height", y.bandwidth())
            .attr("rx", 6)
            .attr("ry", 6)
            .style("fill", "#fff")
            .style("stroke", "transparent")
            .merge(rects) // Update
            .transition().duration(500)
            .style("fill", d => getColor(+d[currentMetric]));

        // Interactions (must re-attach generally or use merge correctly)
        cellsG.selectAll("rect")
            .on("mouseover", function (event, d) {
                d3.select(this)
                    .style("stroke", "#334155")
                    .style("stroke-width", 2)
                    .raise();

                const val = +d[currentMetric];
                const label = isCount ? "Records" : "Avg Speed";
                const fmt = isCount ? d3.format(",") : d => d.toFixed(1) + " km/h";

                tooltip.style("visibility", "visible").html(`
                    <div style="font-weight:800; color:#1e293b; margin-bottom:4px;">${d.Degree_of_congestion}</div>
                    <div style="font-size:12px; color:#64748b; margin-bottom:6px;">Time: ${d.hour}:00</div>
                    <div style="font-size:14px; color:${isCount ? "#e11d48" : "#059669"}; font-weight:bold;">
                        ${label}: ${fmt(val)}
                    </div>
                    ${!isCount ? `<div style="font-size:11px; margin-top:2px; color:#94a3b8">Volume: ${d.count}</div>` : ""}
                `);
            })
            .on("mousemove", function (event) {
                const box = container.getBoundingClientRect();
                tooltip.style("top", (event.clientY - box.top - 40) + "px")
                    .style("left", (event.clientX - box.left + 20) + "px");
            })
            .on("mouseout", function () {
                d3.select(this).style("stroke", "transparent");
                tooltip.style("visibility", "hidden");
            });

        rects.exit().remove();
    }

    // Initial
    updateButtons();
    updateChart();
}
