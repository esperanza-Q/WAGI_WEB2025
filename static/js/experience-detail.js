document.addEventListener('DOMContentLoaded', function() {
  const scrollBox = document.querySelector('.detail-image-scroll');
  const leftBtn = document.querySelector('.image-scroll-btn.left');
  const rightBtn = document.querySelector('.image-scroll-btn.right');
  const img = scrollBox.querySelector('img');
  const scrollAmount = img ? img.offsetWidth + 20 : 260; // 이미지+gap

  leftBtn.addEventListener('click', () => {
    scrollBox.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  });
  rightBtn.addEventListener('click', () => {
    scrollBox.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  });
});
