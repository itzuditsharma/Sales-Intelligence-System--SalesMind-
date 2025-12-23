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
          backgroundColor: data.map(() => "rgba(26,179,148,1)"),
          borderColor: "rgba(26,179,148,1)",
          borderWidth: 1,
          borderRadius: 8,
          borderSkipped: false,
          hoverBackgroundColor: "rgba(26,179,148,1)",
          hoverBorderColor: "rgba(26,179,148,1)"
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: "Proposals count" },
            grid: { display: false }
          },
          x: {
            title: { display: true, text: "Month" },
            grid: { display: false }
          }
        },
        plugins: {
          title: { display: true, text: "Monthly Proposals Data" },
          legend: { display: false }
        }
      }
    });

  } catch (error) {
    console.error("Error loading chart data:", error);
  }
});
