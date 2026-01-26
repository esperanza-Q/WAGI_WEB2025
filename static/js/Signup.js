document.addEventListener("DOMContentLoaded", () => {
  const collegeSelect = document.getElementById("collegeSelect");
  const deptSelect = document.getElementById("deptSelect");
  const form = document.querySelector("form"); // ✅ 일단 가장 확실하게 form 잡기

  console.log("collegeSelect:", !!collegeSelect);
  console.log("deptSelect:", !!deptSelect);
  console.log("form:", form);

  if (!collegeSelect || !deptSelect) return;

  function resetDept(message = "학과 선택") {
    deptSelect.innerHTML = `<option value="" disabled selected>${message}</option>`;
    deptSelect.disabled = true;
  }

  collegeSelect.addEventListener("change", async () => {
    const collegeCode = collegeSelect.value;
    console.log("선택된 단과대:", collegeCode);

    resetDept("불러오는 중...");
    if (!collegeCode) return;

    try {
      const url = `/accounts/api/departments/?college_id=${encodeURIComponent(collegeCode)}`;
      console.log("요청 URL:", url);

      const res = await fetch(url);
      console.log("응답 status:", res.status);
      console.log("content-type:", res.headers.get("content-type"));

      const data = await res.json();
      console.log("응답 data:", data);

      const departments = Array.isArray(data.departments) ? data.departments : [];
      console.log("departments length:", departments.length);

      if (departments.length === 0) {
        resetDept("해당 단과대 학과가 없습니다");
        return;
      }

      deptSelect.disabled = false;
      deptSelect.innerHTML = `<option value="" disabled selected>학과 선택</option>`;

      departments.forEach(d => {
        const opt = document.createElement("option");
        opt.value = d.dept_id;
        opt.textContent = d.dept_name;
        deptSelect.appendChild(opt);
      });
    } catch (e) {
      console.error("학과 목록 불러오기 실패:", e);
      resetDept("학과 목록을 불러오지 못했습니다");
    }
  });

  resetDept();

  if (form) {
    form.addEventListener("submit", () => {
      console.log("submit 직전 dept disabled:", deptSelect.disabled, "value:", deptSelect.value);
      deptSelect.disabled = false;
    });
  }
});
