document.addEventListener('DOMContentLoaded', function() {
  // 파일 업로드 관련 - 업로드된 파일 목록을 따로 저장할 배열 (input.files는 읽기 전용)
  let selectedFiles = [];
  const MAX_FILES = 5; // 최대 업로드 개수

  const input = document.getElementById("recruit-upload-input");
  const preview = document.getElementById("recruit-post-upload-preview");

  // input change 이벤트
  input.addEventListener("change", function(event) {
      const newFiles = Array.from(event.target.files);

      // 파일 최대 개수 제한 체크
      if (selectedFiles.length + newFiles.length > MAX_FILES) {
          alert(`파일은 최대 ${MAX_FILES}개까지 업로드할 수 있습니다.`);
          return;
      }

      // 새 파일들을 배열에 추가
      newFiles.forEach(file => selectedFiles.push(file));

      renderPreview();
  });

  // 미리보기 렌더링 함수
  function renderPreview() {
      preview.innerHTML = ""; // 초기화

      selectedFiles.forEach((file, index) => {
          const item = document.createElement("div");
          item.classList.add("recruit-preview-item");

          // 이미지 파일인지 체크
          if (file.type.startsWith("image/")) {
              const img = document.createElement("img");
              img.classList.add("recruit-preview-img");
              img.src = URL.createObjectURL(file);
              item.appendChild(img);
          } else {
              const fileBox = document.createElement("div");
              fileBox.classList.add("recruit-preview-file");
              fileBox.textContent = file.name;
              item.appendChild(fileBox);
          }

          // 삭제 버튼 추가
          const removeBtn = document.createElement("div");
          removeBtn.classList.add("recruit-preview-remove");
          removeBtn.textContent = "×";

          removeBtn.addEventListener("click", () => {
              selectedFiles.splice(index, 1); // 배열에서 제거
              renderPreview();
          });

          item.appendChild(removeBtn);
          preview.appendChild(item);
      });

      syncInputFiles();
  }

  // 배열을 input.files에 반영
  function syncInputFiles() {
      const dataTransfer = new DataTransfer();
      selectedFiles.forEach(file => dataTransfer.items.add(file));
      input.files = dataTransfer.files;
  }

  // 폼 제출 시 파일 최소 1개 체크
  const form = document.querySelector(".recruit-post-form");

  form.addEventListener("submit", function (e) {
      if (selectedFiles.length === 0) {
          e.preventDefault();
          alert("최소 1개 이상의 사진을 업로드해야 합니다!");
          return;
      }

      // 태그 hidden 값 업데이트
      updateHiddenTags();
  });

  // 태그 저장 관련
  const tagInput = document.getElementById("recruit-tag-input");
  const addTagBtn = document.getElementById("recruit-add-tag-btn");
  const tagList = document.getElementById("recruit-tag-list");
  const hiddenTags = document.getElementById("recruit-hidden-tags");

  let tags = [];

  addTagBtn.addEventListener("click", () => {
      const value = tagInput.value.trim();

      if (!value) return;
      if (tags.includes(value)) return;

      tags.push(value);
      tagInput.value = "";
      renderTags();
  });

  tagInput.addEventListener("keydown", function(e) {
      if (e.key === "Enter") {
          e.preventDefault();
          addTagBtn.click();
      }
  });

  function renderTags() {
      tagList.innerHTML = "";

      tags.forEach((tag, index) => {
          const tagItem = document.createElement("div");
          tagItem.classList.add("recruit-tag-item");
          tagItem.innerHTML = `
              ${tag}
              <span class="recruit-tag-remove" data-index="${index}">×</span>
          `;
          tagList.appendChild(tagItem);
      });

      document.querySelectorAll(".recruit-tag-remove").forEach(btn => {
          btn.addEventListener("click", (e) => {
              const idx = e.target.dataset.index;
              tags.splice(idx, 1);
              renderTags();
          });
      });

      updateHiddenTags();
  }

  function updateHiddenTags() {
      hiddenTags.value = JSON.stringify(tags);  
  }
});
