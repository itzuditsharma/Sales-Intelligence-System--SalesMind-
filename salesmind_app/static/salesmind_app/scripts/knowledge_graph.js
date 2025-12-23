(async () => {
  const graphBody = document.getElementById("graphBody_k");
  const graphModal = document.getElementById("graphModal_k");
  const graphImage = document.getElementById("graphImage_k");
  const modalTitle = document.getElementById("modalTitle_k");
  const closeModal = document.getElementById("closeModal_k");

  try {
    const response = await fetch("/static/salesmind_app/data/projects.json");
    const projects = await response.json();

    projects.forEach((proj) => {
      const row = document.createElement("div");
      row.classList.add("graph-row");
      row.innerHTML = `
        <div>${proj.name}</div>
        <div>${proj.lead}</div>
        <div>${proj.customer}</div>
      `;
      row.addEventListener("click", () => openModal(proj));
      graphBody.appendChild(row);
    });

    function openModal(project) {
      modalTitle.textContent = project.name;
      graphImage.src = project.image;
      graphModal.style.display = "flex";
    }

    closeModal.addEventListener("click", () => {
      graphModal.style.display = "none";
    });

    graphModal.addEventListener("click", (e) => {
      if (e.target === graphModal) graphModal.style.display = "none";
    });
  } catch (err) {
    console.error("Error loading projects:", err);
    graphBody.textContent = "Failed to load projects 😕";
  }
})();
