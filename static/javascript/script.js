const inputs = document.querySelectorAll("input, select");
const progress = document.querySelector(".progress");
const form = document.getElementById("obesityForm");
const btn = document.getElementById("submitBtn");

function updateProgress() {
    const filled = [...inputs].filter(i => i.value).length;
    const percent = (filled / inputs.length) * 100;
    progress.style.width = percent + "%";
}

inputs.forEach(i => i.addEventListener("change", updateProgress));
updateProgress();

form.addEventListener("submit", () => {
    btn.innerHTML = "⏳ Menganalisis Data...";
    btn.disabled = true;
    btn.style.opacity = "0.7";
});
