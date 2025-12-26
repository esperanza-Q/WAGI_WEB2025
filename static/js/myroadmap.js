document.addEventListener("DOMContentLoaded", () => {
  if (!cardsData || cardsData.length === 0) return;

  // 날짜 기준 최신순 정렬
  cardsData.sort((a, b) => {
    if (a.year === b.year) return new Date(b.date) - new Date(a.date);
    return b.year - a.year;
  });

  const container = document.getElementById("roadmap-cards");
  const template = document.getElementById("roadmap-card-template");

  container.innerHTML = "";
  let prevYear = null;

  cardsData.forEach((card, index) => {
    const cardId = card.id ?? index;

    // 연도 라벨
    if (card.year !== prevYear) {
      const yearEl = document.createElement("div");
      yearEl.className = "year-label";
      yearEl.textContent = card.year;
      container.appendChild(yearEl);
      prevYear = card.year;
    }

    // 카드 템플릿 복제
    const clone = template.content.cloneNode(true);
    const cardEl = clone.querySelector(".card");

    // data-id
    cardEl.dataset.id = cardId;

    // 값 채우기
    cardEl.querySelector(".roadmap-card-title").textContent = card.title;
    cardEl.querySelector(".roadmap-category").textContent = card.category;
    cardEl.querySelector(".roadmap-date").textContent = card.date;

    const detailLink = cardEl.querySelector(".roadmap-detail");
    detailLink.href = `./myroadmap-detail.html?id=${encodeURIComponent(cardId)}`;

    // 아코디언
    const header = cardEl.querySelector(".roadmap-card-title");
    const content = cardEl.querySelector(".roadmap-content");

    header.addEventListener("click", () => {
      cardEl.classList.toggle("active");

      if (cardEl.classList.contains("active")) {
        content.style.maxHeight = content.scrollHeight + "px";
      } else {
        content.style.maxHeight = null;
      }
    });

    container.appendChild(clone);
  });
});


