document.addEventListener('DOMContentLoaded', function() {
  // 기존 이미지 슬라이더
  const scrollBox = document.querySelector('.ex-detail-image-scroll');
  const leftBtn = document.querySelector('.ex-image-scroll-btn.left');
  const rightBtn = document.querySelector('.ex-image-scroll-btn.right');
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
