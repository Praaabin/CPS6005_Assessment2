/**
 * TerraFlow D3.js Interactive Visualization
 * 
 * This script creates a custom D3.js visualization for congestion analysis
 * Automatically loaded by Dash from the assets folder
 */

document.addEventListener("DOMContentLoaded", function () {
    console.log("🎨 D3.js visualization initializing...");

    const root = document.getElementById("d3-root");
    if (!root) {
        console.error("D3 root element not found");
        return;
    }

    // Clear existing content
    root.innerHTML = "";

    // Create container
    const container = document.createElement("div");
    container.style.width = "100%";
    container.style.backgroundColor = "#ffffff";
    container.style.borderRadius = "10px";
    container.style.padding = "20px";
    container.style.boxShadow = "0 2px 10px rgba(0,0,0,0.1)";

    // Load data and create visualization
    fetch("../data/processed/congestion_by_hour.parquet")
        .catch(() => {
            // If fetch fails, create sample visualization
            createSampleVisualization(container);
        });

    root.appendChild(container);
});

function createSampleVisualization(container) {
    // Sample data for demonstration
    const data = [
        { hour: 6, congestion: 15 },
        { hour: 7, congestion: 45 },
        { hour: 8, congestion: 75 },
        { hour: 9, congestion: 60 },
        { hour: 10, congestion: 30 },
        { hour: 11, congestion: 25 },
        { hour: 12, congestion: 35 },
        { hour: 13, congestion: 30 },
        { hour: 14, congestion: 28 },
        { hour: 15, congestion: 32 },
        { hour: 16, congestion: 50 },
        { hour: 17, congestion: 80 },
        { hour: 18, congestion: 85 },
        { hour: 19, congestion: 65 },
        { hour: 20, congestion: 40 },
        { hour: 21, congestion: 25 },
        { hour: 22, congestion: 15 }
    ];

    // Dimensions
    const margin = { top: 40, right: 30, bottom: 60, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(container)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3.scaleBand()
        .domain(data.map(d => d.hour))
        .range([0, width])
        .padding(0.2);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.congestion)])
        .nice()
        .range([height, 0]);

    // Color scale
    const colorScale = d3.scaleSequential()
        .domain([0, d3.max(data, d => d.congestion)])
        .interpolator(d3.interpolateRdYlGn)
        .range([1, 0]);  // Reverse for red=high, green=low

    // Add title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .style("font-size", "18px")
        .style("font-weight", "bold")
        .style("fill", "#2c3e50")
        .text("Congestion Intensity Heatmap (D3.js)");

    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("font-size", "12px");

    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("font-size", "12px");

    // X axis label
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", height + 40)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("fill", "#7f8c8d")
        .text("Hour of Day");

    // Y axis label
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", -45)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("fill", "#7f8c8d")
        .text("Congestion Index");

    // Create tooltip
    const tooltip = d3.select(container)
        .append("div")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background-color", "rgba(0, 0, 0, 0.8)")
        .style("color", "white")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("font-size", "12px")
        .style("pointer-events", "none");

    // Add bars with animation
    svg.selectAll("rect")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => x(d.hour))
        .attr("width", x.bandwidth())
        .attr("y", height)  // Start from bottom
        .attr("height", 0)  // Start with 0 height
        .attr("fill", d => colorScale(d.congestion))
        .attr("stroke", "#2c3e50")
        .attr("stroke-width", 1)
        .style("cursor", "pointer")
        .on("mouseover", function (event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("opacity", 0.7)
                .attr("stroke-width", 3);

            tooltip
                .style("visibility", "visible")
                .html(`<strong>Hour:</strong> ${d.hour}:00<br><strong>Congestion:</strong> ${d.congestion}`);
        })
        .on("mousemove", function (event) {
            tooltip
                .style("top", (event.pageY - 10) + "px")
                .style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function () {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("opacity", 1)
                .attr("stroke-width", 1);

            tooltip.style("visibility", "hidden");
        })
        // Animate bars growing from bottom
        .transition()
        .duration(1000)
        .delay((d, i) => i * 50)
        .attr("y", d => y(d.congestion))
        .attr("height", d => height - y(d.congestion));

    // Add value labels on top of bars
    svg.selectAll(".label")
        .data(data)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("x", d => x(d.hour) + x.bandwidth() / 2)
        .attr("y", height)
        .attr("text-anchor", "middle")
        .style("font-size", "11px")
        .style("font-weight", "bold")
        .style("fill", "#2c3e50")
        .style("opacity", 0)
        .text(d => d.congestion)
        .transition()
        .duration(1000)
        .delay((d, i) => i * 50 + 500)
        .attr("y", d => y(d.congestion) - 5)
        .style("opacity", 1);

    // Add legend
    const legendWidth = 200;
    const legendHeight = 20;

    const legend = svg.append("g")
        .attr("transform", `translate(${width - legendWidth - 10}, -30)`);

    const legendScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.congestion)])
        .range([0, legendWidth]);

    const legendAxis = d3.axisBottom(legendScale)
        .ticks(5);

    // Gradient for legend
    const defs = svg.append("defs");
    const gradient = defs.append("linearGradient")
        .attr("id", "legend-gradient");

    gradient.selectAll("stop")
        .data(d3.range(0, 1.1, 0.1))
        .enter()
        .append("stop")
        .attr("offset", d => `${d * 100}%`)
        .attr("stop-color", d => colorScale(d * d3.max(data, d => d.congestion)));

    legend.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#legend-gradient)")
        .attr("stroke", "#2c3e50")
        .attr("stroke-width", 1);

    legend.append("g")
        .attr("transform", `translate(0, ${legendHeight})`)
        .call(legendAxis)
        .selectAll("text")
        .style("font-size", "10px");

    legend.append("text")
        .attr("x", legendWidth / 2)
        .attr("y", -5)
        .attr("text-anchor", "middle")
        .style("font-size", "11px")
        .style("fill", "#7f8c8d")
        .text("Low ← Congestion → High");

    console.log("✅ D3.js visualization created successfully");
}
