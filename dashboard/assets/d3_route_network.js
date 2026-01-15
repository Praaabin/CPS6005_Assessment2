/**
 * D3.js Interactive Route Network & Efficiency Analysis
 * 
 * Features:
 * - Dynamic clustering by Route ID
 * - Dual View Mode: "Network Map" (Force-Directed) vs "Efficiency Matrix" (Scatter)
 * - Zoom/Pan capabilities (Geometric Zooming)
 * - Interactive Highlight & Tooltips
 * - Glassmorphism UI controls
 */

const initNet = setInterval(() => {
    const root = document.getElementById("d3-network-root");
    if (root && window.d3) {
        clearInterval(initNet);
        renderNetwork(root);
    }
}, 300);

async function renderNetwork(root) {
    root.innerHTML = "";

    // -- UI Controls Container --
    const controls = document.createElement("div");
    controls.style.cssText = `
        position: absolute; top: 10px; right: 10px; z-index: 10;
        display: flex; gap: 8px;
    `;

    // Toggle Button Helper
    const createBtn = (id, text, active = false) => {
        const btn = document.createElement("button");
        btn.innerHTML = text;
        btn.id = id;
        btn.className = active ? "active-mode" : "";
        btn.style.cssText = `
            background: ${active ? "#1e3a8a" : "rgba(255,255,255,0.9)"};
            color: ${active ? "#fff" : "#1e293b"};
            border: 1px solid rgba(30,58,138,0.2);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        `;
        btn.onclick = () => {
            controls.querySelectorAll("button").forEach(b => {
                b.style.background = "rgba(255,255,255,0.9)";
                b.style.color = "#1e293b";
                b.classList.remove("active-mode");
            });
            btn.style.background = "#1e3a8a";
            btn.style.color = "#fff";
            btn.classList.add("active-mode");
            updateView(id);
        };
        return btn;
    };

    const btnMap = createBtn("view-map", "🕸️ Network Topology", true);
    const btnEff = createBtn("view-eff", "📉 Efficiency Matrix");

    controls.appendChild(btnMap);
    controls.appendChild(btnEff);
    root.style.position = "relative";
    root.appendChild(controls);

    // -- Chart Container --
    const container = document.createElement("div");
    container.style.width = "100%";
    container.style.height = "100%";
    root.appendChild(container);

    const url = "/assets/data/route_network.json";
    let graph;
    try {
        graph = await d3.json(url);
    } catch (e) {
        container.innerHTML = `<div style="padding:20px;color:#ef4444;font-weight:bold;">❌ Could not load ${url}.</div>`;
        return;
    }

    if (!graph || !graph.nodes || !graph.nodes.length) {
        container.innerHTML = `<div style="padding:20px;">No data available.</div>`;
        return;
    }

    // Process Nodes: Extract "Group" from ID (e.g., NORMAL_149...)
    const nodes = graph.nodes.map(d => {
        // Extract number if possible, e.g. "NORMAL_149" -> "149"
        const match = d.id.match(/_(\d+[A-Z]?)(_|$)/);
        const group = match ? match[1] : "Other";
        return { ...d, group };
    });

    // Filter out "City Hub" for the main viz (it biases the scale) or keep it distinct
    const cityHub = nodes.find(n => n.id === "City Hub");
    // We filter OUT city hub for the scatter plots as it has 0 speed/congestion usually
    const dataNodes = nodes.filter(n => n.id !== "City Hub");

    // Dimensions
    const width = root.clientWidth || 900;
    const height = 480;

    const svg = d3.select(container).append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .style("background", "radial-gradient(circle at center, rgb(255,255,255) 0%, rgb(248,250,252) 100%)")
        .style("border-radius", "12px")
        .style("overflow", "visible");

    // Zoom Group
    const g = svg.append("g");

    const zoom = d3.zoom()
        .scaleExtent([0.5, 4])
        .on("zoom", (event) => g.attr("transform", event.transform));

    svg.call(zoom);

    // Scales
    const maxTrips = d3.max(dataNodes, d => +d.trip_count) || 1;
    const sizeScale = d3.scaleSqrt().domain([0, maxTrips]).range([4, 18]);

    // Color Scale: Low Congestion (Green) -> High (Red)
    // Custom interpolator for Green -> Yellow -> Red
    // Congestion Rate is 0 to 1. Usually < 0.2 is acceptable. > 0.5 is heavy.
    const riskColor = d => d3.interpolateRdYlGn(1 - Math.min(1, (d.congestion_rate || 0) * 4));

    // Efficiency Matrix Scales
    // Avg Speed: 0 to ~60
    const xEff = d3.scaleLinear()
        .domain([0, d3.max(dataNodes, d => d.avg_speed) || 80])
        .range([-width / 2 + 60, width / 2 - 60]);

    // Congestion: 0 to ~0.2
    const yEff = d3.scaleLinear()
        .domain([0, d3.max(dataNodes, d => d.congestion_rate) || 0.5])
        .range([height / 2 - 40, -height / 2 + 40]);

    // Force Simulation
    const simulation = d3.forceSimulation(dataNodes)
        .force("charge", d3.forceManyBody().strength(-30))
        .force("collide", d3.forceCollide().radius(d => sizeScale(d.trip_count) + 2).iterations(2));

    // Center of view
    const cx = width / 2;
    const cy = height / 2;

    // -- AXES (Stats Mode) --
    // We draw them relative to center (0,0) in simulation space if we translate g to center?
    // Actually the simulation nodes have x,y relative to center if we forceCenter?
    // Let's keep simulation centered at 0,0 and translate the <g> to center.
    // That way Zoom works nicely.

    // Adjust simulation forces to be centered at 0,0
    simulation.force("center", d3.forceCenter(0, 0));

    // Initial transform to center
    // We manually set the initial zoom transform to center the 0,0 coordinate
    const initialTransform = d3.zoomIdentity.translate(width / 2, height / 2);
    svg.call(zoom.transform, initialTransform);

    const axisGroup = g.append("g").attr("class", "axis-group").style("opacity", 0);

    // Axis generators
    const xAxis = d3.axisBottom(xEff).ticks(5);
    const yAxis = d3.axisLeft(yEff).ticks(5);

    axisGroup.append("g")
        .attr("transform", `translate(0, ${height / 2 - 40})`) // Bottom of chart area
        .call(xAxis)
        .call(g => g.select(".domain").attr("stroke", "#94a3b8"))
        .call(g => g.selectAll(".tick line").attr("stroke", "#cbd5e1"))
        .call(g => g.selectAll(".tick text").attr("fill", "#64748b"));

    axisGroup.append("g")
        .attr("transform", `translate(${-width / 2 + 60}, 0)`) // Left of chart area
        .call(yAxis)
        .call(g => g.select(".domain").attr("stroke", "#94a3b8"))
        .call(g => g.selectAll(".tick line").attr("stroke", "#cbd5e1"))
        .call(g => g.selectAll(".tick text").attr("fill", "#64748b"));

    // Axis Labels
    axisGroup.append("text")
        .attr("x", 0).attr("y", height / 2 - 5)
        .attr("text-anchor", "middle")
        .style("fill", "#475569").style("font-size", "11px").style("font-weight", "bold")
        .text("Average Speed (km/h) →");

    axisGroup.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", 0).attr("y", -width / 2 + 25)
        .attr("text-anchor", "middle")
        .style("fill", "#475569").style("font-size", "11px").style("font-weight", "bold")
        .text("Congestion Rate (Higher is Worse) →");


    // Tooltip
    const tooltip = d3.select(container).append("div")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "rgba(255, 255, 255, 0.95)")
        .style("backdrop-filter", "blur(4px)")
        .style("padding", "12px")
        .style("border", "1px solid rgba(0,0,0,0.1)")
        .style("border-radius", "8px")
        .style("box-shadow", "0 10px 25px rgba(0,0,0,0.15)")
        .style("pointer-events", "none")
        .style("font-size", "12px")
        .style("color", "#0f172a")
        .style("z-index", 100);

    // -- Render Nodes --
    const circle = g.selectAll("circle")
        .data(dataNodes)
        .join("circle")
        .attr("r", d => sizeScale(d.trip_count || 0))
        .attr("fill", d => riskColor(d))
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .style("cursor", "pointer")
        .style("transition", "fill 0.3s")
        .on("mouseenter", function (event, d) {
            d3.select(this)
                .transition().duration(200)
                .attr("r", sizeScale(d.trip_count || 0) * 1.5)
                .attr("stroke", "#1e293b")
                .attr("stroke-width", 2);

            tooltip.style("visibility", "visible").html(`
                <div style="font-weight:700; color:#1e3a8a; margin-bottom:4px; border-bottom:1px solid #eee; padding-bottom:4px;">${d.id}</div>
                <div style="display:grid; grid-template-columns: auto auto; gap:4px 12px; margin-top:4px;">
                    <span style="color:#64748b">Route Group:</span> <b>${d.group}</b>
                    <span style="color:#64748b">Bus Trips:</span> <b>${d.trip_count}</b>
                    <span style="color:#64748b">Avg Speed:</span> <b>${d.avg_speed.toFixed(1)} km/h</b>
                    <span style="color:#64748b">Congestion:</span> <b style="color:${riskColor(d)}">${(d.congestion_rate * 100).toFixed(1)}%</b>
                </div>
            `);
        })
        .on("mousemove", function (event) {
            // Intelligent positioning to avoid overflow
            const box = container.getBoundingClientRect();
            // Mouse coordinates relative to container
            const mouseX = event.clientX - box.left;
            const mouseY = event.clientY - box.top;

            let left = mouseX + 15;
            let top = mouseY - 10;

            if (left + 220 > box.width) left = mouseX - 230;
            if (top + 100 > box.height) top = mouseY - 110;

            tooltip
                .style("left", left + "px")
                .style("top", top + "px");
        })
        .on("mouseleave", function (e, d) {
            d3.select(this)
                .transition().duration(200)
                .attr("r", sizeScale(d.trip_count || 0))
                .attr("stroke", "#fff")
                .attr("stroke-width", 1.5);
            tooltip.style("visibility", "hidden");
        });

    // Node Labels (Only for large nodes)
    const labels = g.selectAll("text.label")
        .data(dataNodes.filter(d => d.trip_count > maxTrips * 0.4))
        .join("text")
        .attr("class", "label")
        .text(d => d.group) // Use Group ID (Route Number)
        .attr("dy", -10)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .style("font-weight", "700")
        .style("fill", "#334155")
        .style("pointer-events", "none")
        .style("text-shadow", "0 1px 2px white, 0 0 4px white");

    // -- Simulation Logic --
    simulation.on("tick", () => {
        circle
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
        labels
            .attr("x", d => d.x)
            .attr("y", d => d.y - sizeScale(d.trip_count));
    });

    // -- VIEW MODES --
    function updateView(mode) {
        if (mode === "view-map") {
            // Topology Map Mode
            simulation
                .force("x", d3.forceX(0).strength(0.08)) // Cluster in middle
                .force("y", d3.forceY(0).strength(0.08))
                .force("collide", d3.forceCollide().radius(d => sizeScale(d.trip_count) + 4).strength(0.8))
                .alpha(0.3).restart();

            // Hide Axes
            axisGroup.transition().duration(500).style("opacity", 0);

            // Reset Zoom
            svg.transition().duration(750)
                .call(zoom.transform, initialTransform);

        } else {
            // Efficiency Matrix Mode
            simulation
                .force("x", d3.forceX(d => xEff(d.avg_speed)).strength(0.6))
                .force("y", d3.forceY(d => yEff(d.congestion_rate)).strength(0.6))
                .force("collide", d3.forceCollide().radius(d => sizeScale(d.trip_count)).strength(0.5))
                .alpha(0.3).restart();

            // Show Axes
            axisGroup.transition().duration(500).style("opacity", 1);
        }
    }

    // Initial Start
    updateView("view-map");
}
