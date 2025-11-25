// 이미지 슬라이더 (좌우 버튼)
document.addEventListener('DOMContentLoaded', function() {
  const scrollBox = document.querySelector('.recruit-detail-image-scroll');
  const leftBtn = document.querySelector('.recruit-image-scroll-btn.left');
  const rightBtn = document.querySelector('.recruit-image-scroll-btn.right');
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

// 좋아요 버튼 토글
const likeBtn = document.querySelector('.recruit-detail-like-btn');
if (likeBtn) {
  likeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    this.classList.toggle('active');
    const countSpan = this.querySelector('.recruit-detail-like-count');
    if (countSpan) {
      let count = parseInt(countSpan.textContent, 10) || 0;
      count = this.classList.contains('active') ? count + 1 : count - 1;
      countSpan.textContent = count;
    }
  });
}

// 스크랩 버튼 토글
const scrapBtn = document.querySelector('.recruit-scrap-btn');
if (scrapBtn) {
  scrapBtn.addEventListener('click', function (e) {
    e.preventDefault();
    this.classList.toggle('active');
    const img = this.querySelector('img');
    if (img) {
      img.src = this.classList.contains('active') ? '../../static/img/scrap-fill.svg' : '../../static/img/scrap.svg';
    }
  });
}

// 수정/삭제 버튼
const editBtn = document.querySelector('.recruit-edit-btn');
if (editBtn) {
  editBtn.addEventListener('click', function (e) {
    alert('수정 페이지로 이동합니다.');
    // location.href = '수정페이지url';
  });
}
const deleteBtn = document.querySelector('.recruit-delete-btn');
if (deleteBtn) {
  deleteBtn.addEventListener('click', function () {
    if (confirm('정말 삭제하시겠습니까?')) {
      alert('삭제되었습니다.');
      // 실제 삭제 로직 필요
    }
  });
}
