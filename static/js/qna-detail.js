const openBtn = document.getElementById("openModalBtn");
const closeBtn = document.getElementById("closeModalBtn");
const modal = document.getElementById("answerModal");
const form = document.getElementById("answerForm");

function openModal() {
  if (!modal) return;
  modal.style.display = "flex";
}

function closeModal() {
  if (!modal) return;
  modal.style.display = "none";
}

if (openBtn) {
  openBtn.addEventListener("click", openModal);
}

if (closeBtn) {
  closeBtn.addEventListener("click", closeModal);
}

// backdrop 클릭 시 닫기
if (modal) {
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
}

// 연동 전: submit 막기
if (form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault(); // 서버로 안 보냄, 연동할 때 지워주시면 됩니다
    closeModal();
  });
}



