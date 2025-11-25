const OtherQnAtextarea = document.querySelector(".otherQnA-post-bottom-detail textarea")

//사용자가 입력한 값만큼 height 증가
OtherQnAtextarea.addEventListener("input", () => {
    OtherQnAtextarea.style.height = "auto";
    OtherQnAtextarea.style.height = OtherQnAtextarea.scrollHeight + "px";
});