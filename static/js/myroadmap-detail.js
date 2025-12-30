document.addEventListener('DOMContentLoaded', function() {
  // 기존 이미지 슬라이더
  const scrollBox = document.querySelector('.roadmap-detail-image-scroll');
  const leftBtn = document.querySelector('.roadmap-image-scroll-btn.left');
  const rightBtn = document.querySelector('.roadmap-image-scroll-btn.right');
  const img = scrollBox ? scrollBox.querySelector('img') : null;
  const scrollAmount = img ? img.offsetWidth + 20 : 260; // 이미지+gap

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


// 수정/삭제 버튼 (예시: 실제 구현 시 서버 연동 필요)
const editBtn = document.querySelector('.roadmap-edit-btn');
if (editBtn) {
  editBtn.addEventListener('click', function () {
    alert('수정 페이지로 이동합니다.');
    // location.href = '수정페이지url';
  });
}
const deleteBtn = document.querySelector('.roadmap-delete-btn');
if (deleteBtn) {
  deleteBtn.addEventListener('click', function () {
    if (confirm('정말 삭제하시겠습니까?')) {
      alert('삭제되었습니다.');
      // 실제 삭제 로직 필요
    }
  });
}
