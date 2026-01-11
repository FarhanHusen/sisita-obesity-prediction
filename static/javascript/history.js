document.addEventListener("DOMContentLoaded", () => {

    const searchInput = document.getElementById("searchInput");
    const pagination = document.getElementById("pagination");
    const allRows = Array.from(document.querySelectorAll("tbody tr"));

    if (!searchInput || !pagination || allRows.length === 0) return;

    const rowsPerPage = 8;
    let currentPage = 1;
    let filteredRows = [...allRows];

    // =========================
    // SIMPAN HTML ASLI SETIAP TD
    // =========================
    allRows.forEach(row => {
        row.querySelectorAll("td").forEach(td => {
            td.dataset.originalHtml = td.innerHTML;
        });
    });

    // =========================
    // RENDER TABLE
    // =========================
    function renderTable() {
        allRows.forEach(row => row.style.display = "none");

        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        filteredRows.slice(start, end).forEach(row => {
            row.style.display = "";
        });
    }

    // =========================
    // PAGINATION
    // =========================
    function renderPagination() {
        pagination.innerHTML = "";
        const totalPages = Math.ceil(filteredRows.length / rowsPerPage);
        if (totalPages <= 1) return;

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");
            btn.textContent = i;
            btn.className = "page-btn";
            if (i === currentPage) btn.classList.add("active");

            btn.addEventListener("click", () => {
                currentPage = i;
                renderTable();
                renderPagination();
            });

            pagination.appendChild(btn);
        }
    }

    // =========================
    // RESET HIGHLIGHT (FULL AMAN)
    // =========================
    function resetHighlight() {
        allRows.forEach(row => {
            row.querySelectorAll("td").forEach(td => {
                td.innerHTML = td.dataset.originalHtml;
            });
        });
    }

    // =========================
    // SEARCH + HIGHLIGHT
    // =========================
    searchInput.addEventListener("input", () => {
        const keyword = searchInput.value.trim().toLowerCase();
        currentPage = 1;

        resetHighlight();

        filteredRows = allRows.filter(row =>
            row.textContent.toLowerCase().includes(keyword)
        );

        if (keyword) {
            filteredRows.forEach(row => {
                const tds = row.querySelectorAll("td");

                tds.forEach((td, index) => {
                    // ❗ JANGAN SENTUH kolom Hapus
                    if (index === tds.length - 1) return;

                    const text = td.textContent;
                    const regex = new RegExp(`(${keyword})`, "gi");
                    td.innerHTML = text.replace(regex, "<mark>$1</mark>");
                });
            });
        }

        renderTable();
        renderPagination();
    });

    // =========================
    // INIT
    // =========================
    renderTable();
    renderPagination();

});
