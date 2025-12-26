// 파일 업로드 관련 - 업로드된 파일 목록을 따로 저장할 배열 (input.files는 읽기 전용)
let selectedFiles = [];
const MAX_FILES = 5; // 최대 업로드 개수

const input = document.getElementById("roadmap-upload-input");
const preview = document.getElementById("roadmap-upload-preview");

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
        item.classList.add("roadmap-preview-item");

        // 이미지 파일인지 체크
        if (file.type.startsWith("image/")) {
            const img = document.createElement("img");
            img.classList.add("roadmap-preview-img");
            img.src = URL.createObjectURL(file);
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("roadmap-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }

        // 삭제 버튼 추가
        const removeBtn = document.createElement("div");
        removeBtn.classList.add("roadmap-preview-remove");
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
const form = document.querySelector(".roadmap-post-form");

form.addEventListener("submit", function (e) {
    if (selectedFiles.length === 0) {
        e.preventDefault();
        alert("최소 1개 이상의 사진을 업로드해야 합니다!");
        return;
    }
});