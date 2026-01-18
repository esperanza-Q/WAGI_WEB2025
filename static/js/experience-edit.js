let selectedFiles = [];
let deletedFiles = [];
const MAX_FILES = 5;

const input = document.getElementById("ex-edit-upload-input");
const preview = document.getElementById("ex-edit-upload-preview");
const deletedFilesInput = document.getElementById("ex-deleted-files");
const form = document.querySelector(".ex-edit-form");

document
  .querySelectorAll(".ex-edit-preview-remove[data-file-id]")
  .forEach(btn => {
    btn.addEventListener("click", () => {
      const fileId = btn.dataset.fileId;

      deletedFiles.push(fileId);
      deletedFilesInput.value = JSON.stringify(deletedFiles);

      // 화면에서 제거
      btn.parentElement.remove();
    });
  });

input.addEventListener("change", function (event) {
  const newFiles = Array.from(event.target.files);

  const existingCount =
    document.querySelectorAll(".ex-edit-preview-remove[data-file-id]").length;

  if (existingCount + selectedFiles.length + newFiles.length > MAX_FILES) {
    alert(`파일은 최대 ${MAX_FILES}개까지 업로드할 수 있습니다.`);
    return;
  }

  newFiles.forEach(file => {
    selectedFiles.push(file);
    appendNewFilePreview(file, selectedFiles.length - 1);
  });

  syncInputFiles();
});

function appendNewFilePreview(file, index) {
  const item = document.createElement("div");
  item.classList.add("ex-edit-preview-item");

  if (file.type.startsWith("image/")) {
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.classList.add("ex-edit-preview-img");
    item.appendChild(img);
  } else {
    const fileBox = document.createElement("div");
    fileBox.textContent = file.name;
    fileBox.classList.add("ex-edit-preview-file");
    item.appendChild(fileBox);
  }

  const removeBtn = document.createElement("div");
  removeBtn.textContent = "×";
  removeBtn.classList.add("ex-edit-preview-remove");
  removeBtn.addEventListener("click", () => {
    selectedFiles.splice(index, 1);
    item.remove();
    syncInputFiles();
  });

  item.appendChild(removeBtn);
  preview.appendChild(item);
}

function syncInputFiles() {
  const dataTransfer = new DataTransfer();
  selectedFiles.forEach(file => dataTransfer.items.add(file));
  input.files = dataTransfer.files;
}

// 태그 처리

const hiddenTagsInput = document.getElementById("ex-edit-hidden-tags");
const tagInput = document.getElementById("ex-edit-tag-input");
const addTagBtn = document.getElementById("ex-edit-add-tag-btn");
const tagList = document.getElementById("ex-edit-tag-list");

// 서버에서 내려준 태그로 초기화
let tags = hiddenTagsInput.value
  ? hiddenTagsInput.value.split(",").map(t => t.trim()).filter(Boolean)
  : [];

addTagBtn.addEventListener("click", () => {
  const value = tagInput.value.trim();
  if (!value) return;
  if (tags.includes(value)) return;

  tags.push(value);
  tagInput.value = "";
  renderTags();
});

tagInput.addEventListener("keydown", e => {
  if (e.key === "Enter") {
    e.preventDefault();
    addTagBtn.click();
  }
});

function renderTags() {
  tagList.innerHTML = "";

  tags.forEach((tag, index) => {
    const tagItem = document.createElement("div");
    tagItem.classList.add("ex-edit-tag-item");
    tagItem.innerHTML = `
      ${tag}
      <span class="ex-edit-tag-remove" data-index="${index}">×</span>
    `;
    tagList.appendChild(tagItem);
  });

  document.querySelectorAll(".ex-edit-tag-remove").forEach(btn => {
    btn.addEventListener("click", e => {
      const idx = e.target.dataset.index;
      tags.splice(idx, 1);
      renderTags();
    });
  });

  hiddenTagsInput.value = tags.join(",");
}

// 최초 태그 렌더
renderTags();

// submit 시 최종 검증
form.addEventListener("submit", function (e) {
  const remainingExistingFiles =
    document.querySelectorAll(".ex-edit-preview-remove[data-file-id]").length;

  if (remainingExistingFiles + selectedFiles.length === 0) {
    e.preventDefault();
    alert("최소 1개 이상의 파일을 업로드해야 합니다!");
    return;
  }

  hiddenTagsInput.value = tags.join(",");
});

