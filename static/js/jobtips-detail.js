// 좋아요 버튼 토글
/*const likeBtn = document.querySelector('.jobtips-detail-like-btn');
if (likeBtn) {
  likeBtn.addEventListener('click', function () {
    this.classList.toggle('active');
    const countSpan = this.querySelector('.jobtips-detail-like-count');
    if (countSpan) {
      let count = parseInt(countSpan.textContent, 10) || 0;
      count = this.classList.contains('active') ? count + 1 : count - 1;
      countSpan.textContent = count;
    }
  });
}

// 스크랩 버튼 토글
const scrapBtn = document.querySelector('.jobtips-scrap-icon');
if (scrapBtn) {
  scrapBtn.addEventListener('click', function () {
    this.classList.toggle('active');
  });
}

// 수정/삭제 버튼
const editBtn = document.querySelector('.jobtips-edit-btn');
if (editBtn) {
  editBtn.addEventListener('click', function () {
    alert('수정 페이지로 이동합니다.');
    // location.href = '수정페이지url';
  });
}
const deleteBtn = document.querySelector('.jobtips-delete-btn');
if (deleteBtn) {
  deleteBtn.addEventListener('click', function () {
    if (confirm('정말 삭제하시겠습니까?')) {
      alert('삭제되었습니다.');
      // 실제 삭제 로직 필요
    }
  });
}*/

// 이미지 슬라이더 (좌우 버튼)
document.addEventListener('DOMContentLoaded', function() {
  // 기존 이미지 슬라이더 (jobtips용 클래스명으로 적용)
  const scrollBox = document.querySelector('.jobtips-detail-image-scroll');
  const leftBtn = document.querySelector('.jobtips-image-scroll-btn.left');
  const rightBtn = document.querySelector('.jobtips-image-scroll-btn.right');
  const img = scrollBox ? scrollBox.querySelector('img') : null;
  const scrollAmount = img ? img.offsetWidth + 20 : 260;

  if (leftBtn && scrollBox) {
    leftBtn.addEventListener('click', () => {
      scrollBox.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
  }
  if (rightBtn && scrollBox) {
    rightBtn.addEventListener('click', () => {
      scrollBox.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
  }
});
