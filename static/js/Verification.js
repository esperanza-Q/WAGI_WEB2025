const VerifyImgInput = document.querySelector('.verify-img-input')
const VerifyUploadArea = document.querySelector('.verify-img-upload')
const VerifyPreviewArea = document.querySelector('.verify-img-preview')
const VerifyUploadBtn = document.querySelector('.verify-img-btn')
const VerifyPreviewImg = document.querySelector('.verify-preview-img')
const VerifyResetBtn = document.querySelector('.verify-reset-btn')

//업로드 버튼 클릭 --> 파일 선택창 열기
VerifyUploadBtn.addEventListener('click', () => VerifyImgInput.click());

//파일 선택(change 이벤트) --> 프리뷰 이미지O, 업로드 버튼X
VerifyImgInput.addEventListener('change', (event)=>{
    const file = event.target.files[0];

    if (file){
        VerifyPreviewImg.src = URL.createObjectURL(file);
        
        VerifyUploadArea.style.display="none";
        VerifyPreviewArea.style.display="flex";
    }
});

//초기화 버튼 클릭 --> 프리뷰 이미지X, 업로드 버튼O
VerifyResetBtn.addEventListener('click', () => {
    VerifyImgInput.value="";
    VerifyPreviewImg.src="";

    VerifyPreviewArea.style.display="none";
    VerifyUploadArea.style.display="flex";
});