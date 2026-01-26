// 파일 업로드 관련 - 기존 파일/이미지 + 새로 업로드된 파일 모두 관리
// 파일 - 실제 id 값 연결 필요할 듯 합니다..
let existingFiles = [];  // BE수정- 더미데이터 빈 리스트로 만들었습니다
let selectedFiles = [];
let deletedFiles = [];
const MAX_FILES = 5; // 최대 업로드 개수

const input = document.getElementById("roadmap-edit-upload-input");
const preview = document.getElementById("roadmap-edit-upload-preview");
const deletedFilesInput = document.getElementById("roadmap-deleted-files");

// input change 이벤트
input.addEventListener("change", function (event) {
    const newFiles = Array.from(event.target.files);

    // ✅ 서버 렌더된 기존 이미지 개수 (DOM 기준)
    const existingCount =
        document.querySelectorAll(
            "#roadmap-edit-upload-preview .existing-item"
        ).length;

    // 🔒 최대 개수 제한 (기존 + 이미 선택 + 새로 선택)
    if (existingCount + selectedFiles.length + newFiles.length > MAX_FILES) {
        alert(`파일은 최대 ${MAX_FILES}개까지 업로드할 수 있습니다.`);
        input.value = "";
        return;
    }

    // ✅ 덮어쓰기 방지: 기존 selectedFiles 유지 + 새 파일 누적
    newFiles.forEach(file => {
        const duplicated = selectedFiles.some(
            f => f.name === file.name && f.size === file.size
        );
        if (!duplicated) {
            selectedFiles.push(file);
        }
    });

    // ✅ 새 파일 미리보기 갱신
    renderPreview();
});

// 미리보기 렌더링 함수
function renderPreview() {
    const livePreview = document.getElementById("live-preview");
    if (!livePreview) return;

    // ✅ 새 파일 미리보기 영역만 초기화
    livePreview.innerHTML = "";

    // ===============================
    // 기존 파일/이미지 (BE 연동 전)
    // ===============================
    existingFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.classList.add("roadmap-edit-preview-item");

        if (file.type === "image") {
            const img = document.createElement("img");
            img.classList.add("roadmap-edit-preview-img");
            img.src = file.url;
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("roadmap-edit-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }

        const removeBtn = document.createElement("div");
        removeBtn.classList.add("roadmap-edit-preview-remove");
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

    // ===============================
    // 새로 업로드한 파일 미리보기
    // ===============================
    selectedFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.classList.add("roadmap-edit-preview-item");

        if (file.type.startsWith("image/")) {
            const img = document.createElement("img");
            img.classList.add("roadmap-edit-preview-img");
            img.src = URL.createObjectURL(file);
            item.appendChild(img);
        } else {
            const fileBox = document.createElement("div");
            fileBox.classList.add("roadmap-edit-preview-file");
            fileBox.textContent = file.name;
            item.appendChild(fileBox);
        }

        const removeBtn = document.createElement("div");
        removeBtn.classList.add("roadmap-edit-preview-remove");
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => {
            selectedFiles.splice(index, 1);
            renderPreview();
        });

        item.appendChild(removeBtn);
        livePreview.appendChild(item);
    });

    syncInputFiles();
}

// 배열을 input.files에 반영
function syncInputFiles() {
    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    input.files = dataTransfer.files;
}

// 폼 제출 시 파일 최소 1개 체크 (수정 페이지 기준)
const form = document.querySelector(".roadmap-edit-form");

form.addEventListener("submit", function (e) {
    const existingCount =
        document.querySelectorAll(
            "#roadmap-edit-upload-preview .existing-item"
        ).length;

    if (existingCount + selectedFiles.length === 0) {
        e.preventDefault();
        alert("최소 1개 이상의 파일을 업로드해야 합니다!");
        return;
    }

    hiddenTagsInput.value = JSON.stringify(tags);
});

// 초기 렌더링
renderPreview();
