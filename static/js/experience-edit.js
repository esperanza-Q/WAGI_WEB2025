// 파일 업로드 관련 - 기존 파일/이미지 + 새로 업로드된 파일 모두 관리
let existingFiles = [
  { name: "sample-img.png", url: "../../static/img/sample-img.png", type: "image" },
  { name: "기존파일.pdf", url: "../../static/files/기존파일.pdf", type: "file" }
];
let selectedFiles = [];
let deletedFiles = [];
const MAX_FILES = 5; // 최대 업로드 개수

const input = document.getElementById("ex-edit-upload-input");
const preview = document.getElementById("ex-edit-upload-preview");
const deletedFilesInput = document.getElementById("ex-deleted-files"); 

// input change 이벤트
input.addEventListener("change", function(event) {
    const newFiles = Array.from(event.target.files);

    // 파일 최대 개수 제한 체크 (기존+신규 합산)
    if (existingFiles.length + selectedFiles.length + newFiles.length > MAX_FILES) {
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

    // 기존 파일/이미지
    existingFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.classList.add("ex-edit-preview-item");
        if (file.type === "image") {
            const img = document.createElement("img");
            img.classList.add("ex-edit-preview-img");
            img.src = file.url;
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("ex-edit-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }
        // 삭제 버튼
        const removeBtn = document.createElement("div");
        removeBtn.classList.add("ex-edit-preview-remove");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => {
            deletedFiles.push(file.id);
            deletedFilesInput.value = JSON.stringify(deletedFiles);

            existingFiles.splice(index, 1);
            renderPreview();
        });
        item.appendChild(removeBtn);
        preview.appendChild(item);
    });

    // 새로 업로드한 파일
    selectedFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.classList.add("ex-edit-preview-item");
        if (file.type.startsWith("image/")) {
            const img = document.createElement("img");
            img.classList.add("ex-edit-preview-img");
            img.src = URL.createObjectURL(file);
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("ex-edit-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }
        // 삭제 버튼
        const removeBtn = document.createElement("div");
        removeBtn.classList.add("ex-edit-preview-remove");
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

// 배열을 input.files에 반영
function syncInputFiles() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    input.files = dataTransfer.files;
}

// 폼 제출 시 파일 최소 1개 체크
const form = document.querySelector(".ex-edit-form");

form.addEventListener("submit", function (e) {
    if (existingFiles.length + selectedFiles.length === 0) {
        e.preventDefault();
        alert("최소 1개 이상의 파일을 업로드해야 합니다!");
        return;
    }
    // 태그 hidden 값 업데이트 (필요시)
    // hiddenTags.value = JSON.stringify(tags);
});

// 태그 저장 관련 - 기존 태그 + 신규 태그
let tags = ["#동아리", "#컴공"];
const tagInput = document.getElementById("ex-edit-tag-input");
const addTagBtn = document.getElementById("ex-edit-add-tag-btn");
const tagList = document.getElementById("ex-edit-tag-list");

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
        tagItem.classList.add("ex-edit-tag-item");
        tagItem.innerHTML = `
            ${tag}
            <span class="ex-edit-tag-remove" data-index="${index}">×</span>
        `;
        tagList.appendChild(tagItem);
    });
    document.querySelectorAll(".ex-edit-tag-remove").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = e.target.dataset.index;
            tags.splice(idx, 1);
            renderTags();
        });
    });
    // updateHiddenTags(); // 필요시
}

// 초기 렌더링
renderPreview();
renderTags();
