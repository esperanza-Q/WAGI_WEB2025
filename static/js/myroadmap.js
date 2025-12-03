document.addEventListener("DOMContentLoaded", () => {

  // 데이터가 없으면 종료
  if (!cardsData || cardsData.length === 0) return;

  // 날짜 기반 최신순 정렬
  cardsData.sort((a, b) => {
    if (a.year === b.year) return new Date(b.date) - new Date(a.date);
    return b.year - a.year;
  });

  const container = document.getElementById("cards");
  container.innerHTML = "";

  let prevYear = null;

  cardsData.forEach(card => {

    // 연도 바뀔 때만 라벨 생성
    if (card.year !== prevYear) {
      const yearEl = document.createElement("div");
      yearEl.className = "year-label";
      yearEl.textContent = card.year;
      container.appendChild(yearEl);
      prevYear = card.year;
    }

    // 카드 생성
    const cardEl = document.createElement("div");
    cardEl.className = "card accordion";
    cardEl.innerHTML = `
      <div class="card-header">${card.title}</div>
      <div class="content">
        <div class="meta">
          <div class="tag">${card.category}</div>
          <div class="date">${card.date}</div>
          <div class="detail-link">상세보기 ></div>
        </div>
      </div>
    `;

    container.appendChild(cardEl);
  });

  // 아코디언 활성화
  document.querySelectorAll(".card").forEach(card => {
    const header = card.querySelector(".card-header");
    const content = card.querySelector(".content");

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

