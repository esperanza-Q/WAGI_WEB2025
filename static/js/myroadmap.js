document.addEventListener("DOMContentLoaded", () => {

  // 데이터가 없으면 종료
  if (!cardsData || cardsData.length === 0) return;

  // 날짜 기반 최신순 정렬
  cardsData.sort((a, b) => {
    if (a.year === b.year) return new Date(b.date) - new Date(a.date);
    return b.year - a.year;
  });

  const container = document.getElementById("roadmap-cards");
  container.innerHTML = "";

  let prevYear = null;

  // index 추가
  cardsData.forEach((card, index) => {

    // 연도 바뀔 때만 라벨 생성
    if (card.year !== prevYear) {
      const yearEl = document.createElement("div");
      yearEl.className = "year-label";
      yearEl.textContent = card.year;
      container.appendChild(yearEl);
      prevYear = card.year;
    }

    // 카드 생성 (상세보기에 data-id 포함)
    const cardEl = document.createElement("div");
    cardEl.className = "card accordion";
    // data-id 속성 추가 (card.id 없으면 index 사용)
    cardEl.dataset.id = card.id ?? index;
    cardEl.innerHTML = `
      <div class="roadmap-card-title">${card.title}</div>
      <div class="roadmap-content">
        <div class="roadmap-meta">
          <div class="roadmap-category">${card.category}</div>
          <div class="roadmap-date">${card.date}</div>
          <a href="./myroadmap-detail.html?id=${encodeURIComponent(card.id ?? index)}"
          class="roadmap-detail"
          data-id="${card.id ?? index}">
          상세보기 &gt;</a>
        </div>
      </div>
    `;

    container.appendChild(cardEl);
  });

  // 아코디언 및 상세보기 네비게이션 처리
  container.querySelectorAll(".card").forEach(card => {
    const header = card.querySelector(".roadmap-card-title");
    const content = card.querySelector(".roadmap-content");

    // 기존 아코디언 로직
    header.addEventListener("click", () => {
      card.classList.toggle("active");

      if (card.classList.contains("active")) {
        content.style.maxHeight = content.scrollHeight + "px";
      } else {
        content.style.maxHeight = null;
      }
    });
  });

});

