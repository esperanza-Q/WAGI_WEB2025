document.addEventListener("DOMContentLoaded", () => {
  const collegeSelect = document.getElementById("collegeSelect");
  const deptSelect = document.getElementById("deptSelect");

  if (!collegeSelect || !deptSelect) return; // 안전장치

  function resetDept() {
    deptSelect.innerHTML = `<option value="" disabled selected>학과 선택</option>`;
    deptSelect.disabled = true;
  }

  collegeSelect.addEventListener("change", async () => {
    const collegeId = collegeSelect.value;
    resetDept();
    if (!collegeId) return;

    const res = await fetch(`/accounts/api/departments/?college_id=${encodeURIComponent(collegeId)}`);
    const data = await res.json();

    data.departments.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d.dept_id;
      opt.textContent = d.dept_name;
      deptSelect.appendChild(opt);
    });

    deptSelect.disabled = data.departments.length === 0;
  });

  resetDept();
});
