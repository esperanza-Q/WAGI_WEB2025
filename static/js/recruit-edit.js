// recruit-edit 페이지용 파일/태그 관리 JS (jobtips-edit에서 recruit-edit 네이밍으로 변경)
// 파일 - 실제 id 값 연결 필요할 듯 합니다..
let existingFiles = [
  { name: "sample-img.png", url: "../../static/img/sample-img.png", type: "image" },
  { name: "기존파일.pdf", url: "../../static/files/기존파일.pdf", type: "file" }
];
let selectedFiles = [];
let deletedFiles = [];
const MAX_FILES = 5;

const input = document.getElementById("recruit-edit-upload-input");
const preview = document.getElementById("recruit-edit-upload-preview");
const deletedFilesInput = document.getElementById("recruit-deleted-files");

input.addEventListener("change", function(event) {
    const newFiles = Array.from(event.target.files);
    if (existingFiles.length + selectedFiles.length + newFiles.length > MAX_FILES) {
        alert(`파일은 최대 ${MAX_FILES}개까지 업로드할 수 있습니다.`);
        return;
    }
    newFiles.forEach(file => selectedFiles.push(file));
    renderPreview();
});

function renderPreview() {
    preview.innerHTML = "";
    existingFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.classList.add("recruit-edit-preview-item");
        if (file.type === "image") {
            const img = document.createElement("img");
            img.classList.add("recruit-edit-preview-img");
            img.src = file.url;
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("recruit-edit-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }
        const removeBtn = document.createElement("div");
        removeBtn.classList.add("recruit-edit-preview-remove");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => {
            deletedFiles.push(file.name);
            deletedFilesInput.value = JSON.stringify(deletedFiles);
            existingFiles.splice(index, 1);
            renderPreview();
        });
        item.appendChild(removeBtn);
        preview.appendChild(item);
    });
    selectedFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.classList.add("recruit-edit-preview-item");
        if (file.type.startsWith("image/")) {
            const img = document.createElement("img");
            img.classList.add("recruit-edit-preview-img");
            img.src = URL.createObjectURL(file);
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("recruit-edit-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }
        const removeBtn = document.createElement("div");
        removeBtn.classList.add("recruit-edit-preview-remove");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => {
            selectedFiles.splice(index, 1);
            renderPreview();
        });
        item.appendChild(removeBtn);
        preview.appendChild(item);
    });
    syncInputFiles();
}

function syncInputFiles() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    input.files = dataTransfer.files;
}

const form = document.querySelector(".recruit-edit-form");
const hiddenTagsInput = document.getElementById("recruit-edit-hidden-tags");

form.addEventListener("submit", function (e) {
    if (existingFiles.length + selectedFiles.length === 0) {
        e.preventDefault();
        alert("최소 1개 이상의 파일을 업로드해야 합니다!");
        return;
    }
    hiddenTagsInput.value = JSON.stringify(tags);
});

// 태그 저장 관련 - 기존 태그 + 신규 태그
let tags = ["#모집", "#스터디"];
const tagInput = document.getElementById("recruit-edit-tag-input");
const addTagBtn = document.getElementById("recruit-edit-add-tag-btn");
const tagList = document.getElementById("recruit-edit-tag-list");

addTagBtn.addEventListener("click", () => {
    const value = tagInput.value.trim();
    if (!value) return;
    if (tags.includes(value)) return;
    tags.push(value);
    tagInput.value = "";
    renderTags();
});

function renderTags() {
    tagList.innerHTML = "";
    tags.forEach((tag, index) => {
        const tagItem = document.createElement("div");
        tagItem.classList.add("recruit-edit-tag-item");
        tagItem.innerHTML = `
            ${tag}
            <span class="recruit-edit-tag-remove" data-index="${index}">×</span>
        `;
        tagList.appendChild(tagItem);
    });
    document.querySelectorAll(".recruit-edit-tag-remove").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = e.target.dataset.index;
            tags.splice(idx, 1);
            renderTags();
        });
    });
    hiddenTagsInput.value = JSON.stringify(tags);
}

renderPreview();
renderTags();
