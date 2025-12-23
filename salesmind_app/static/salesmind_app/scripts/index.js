// Display current datetime
const dt = new Date();
document.getElementById("datetime").textContent = dt.toLocaleString();

// ====================== Proposal Chart ======================
document.addEventListener("DOMContentLoaded", async () => {
  const ctx = document.getElementById("salesChart").getContext("2d");

  try {
    const response = await fetch("/static/salesmind_app/data/proposal_data.json");
    const jsonData = await response.json();

    const labels = Object.keys(jsonData);
    const data = Object.values(jsonData);

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Proposals per Month",
          data: data,
          backgroundColor: Array(data.length).fill("#1ab394"),
          borderColor: "#1ab394",
          borderWidth: 1,
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: "Proposals count" },
          },
          x: {
            title: { display: true, text: "Month" },
            grid: { display: false }
          }
        },
        plugins: {
          title: { display: true, text: "Monthly Proposals Data" },
          legend: { position: "top" }
        }
      }
    });

  } catch (error) {
    console.error("Error loading chart data:", error);
  }
});



// ====================== Objections Chart ======================
fetch("/objections_summary/")
  .then(res => res.json())
  .then(data => {
    const ctx = document.getElementById("objectionsChart").getContext('2d');
    
    const labels = Object.keys(data);      
    const counts = Object.values(data);   

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#4BC0C0','#9966FF'],
          borderWidth: 2
        }]
      },
      options: { 
        responsive: true, 
        plugins: { legend: { position: 'right' } } 
      }
    });
  })
  .catch(err => console.error("Error loading objections data:", err));

// ====================== Highlights ======================
fetch(STATIC_BASE + "project_highlights.json")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("highlightCards");

    // Loop through key–value pairs
    Object.entries(data).forEach(([title, summary]) => {
      const card = document.createElement("div");
      card.className = "highlight-card";
      card.innerHTML = `
        <h4 class="highlight-title">${title}</h4>
        <p class="highlight-summary">${summary}</p>
      `;
      container.appendChild(card);
    });
  })
  .catch(err => console.error("Error loading highlights:", err));

// ====================== Trending Projects ======================
// fetch(STATIC_BASE + "trending.json")
//   .then(res => res.json())
//   .then(data => {
//     const container = document.getElementById("trendingCards");
//     data.projects.forEach(project => {
//       const card = document.createElement("div");
//       card.className = "trending-card";
//       card.innerHTML = `<i class="fa-solid fa-angle-right"></i><p>${project}</p>`;
//       container.appendChild(card);
//     });
//   })
//   .catch(err => console.error("Error loading trending projects:", err));

// ====================== Competitors Chart ======================
document.addEventListener("DOMContentLoaded", function() {

    // + new Date().getTime()
    fetch(STATIC_BASE + "deals_lost.json") // prevent caching
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("heatmapChart");
            if (!ctx) return console.error("Canvas not found");

            const labels = data.competitors.map(c => c.name);
            const dealsLost = data.competitors.map(c => c.deals_lost);

            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Deals Lost",
                        data: dealsLost,
                        backgroundColor: dealsLost.map(val => `rgba(95,118,232,${0.3 + (val / Math.max(...dealsLost)) * 0.7})`),
                        borderColor: "rgba(95,118,232,1)",
                        borderWidth: 1
                    }]
                },
                options: { 
                    indexAxis: 'y', 
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: ctx => `${ctx.label}: ${ctx.raw} deals lost`
                            }
                        }
                    },
                    scales: {
                        x: { beginAtZero: true, title: { display: true, text: 'Deals Lost' } },
                        y: { title: { display: true, text: 'Competitors' } }
                    }
                }
            });
        })
        .catch(err => console.error("Error loading heatmap data:", err));
});
