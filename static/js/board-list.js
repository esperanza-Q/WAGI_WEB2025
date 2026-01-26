// form, hidden input 가져오기
const form = document.getElementById("filter-form");
const categoryInput = document.getElementById("filter-category");
const orderingInput = document.getElementById("filter-ordering");

// 1. 카테고리 탭 클릭 → hidden 변경 → submit
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const category = btn.dataset.category;
    categoryInput.value = category;
    form.submit();
  });
});

// 2. 정렬 탭 클릭 → hidden 변경 → submit
document.querySelectorAll(".order-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const order = btn.dataset.order;
    orderingInput.value = order;
    form.submit();
  });
});

// 3. 선택된 상태 표시 (백엔드 값 유지)
function applyActiveStyles() {
  const currentCategory = categoryInput.value;
  const currentOrdering = orderingInput.value;

  // 카테고리 active
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.category === currentCategory);
  });

  // 정렬 active
  document.querySelectorAll(".order-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.order === currentOrdering);
  });
}

applyActiveStyles();
