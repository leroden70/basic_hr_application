document.addEventListener("submit", async function(e) {
    if (e.target.id === "job_form") {
        e.preventDefault();

        const formData = new FormData(e.target);
        obj = Object.fromEntries(formData.entries());
        const myArray = Object.values(obj)
        cur_employee_id = myArray[0]
        cur_job_id = myArray[1]
        cur_hire_date = myArray[2]
        cur_department_id = myArray[3]
        new_job_id = myArray[4]
        arg = [cur_employee_id, cur_job_id, cur_hire_date, cur_department_id, new_job_id]

        await performOperation('update_job', arg, true)
        await performOperation('employee_list');
        await performOperation('details_dialog', parseInt(cur_employee_id));
        await performOperation('job_dialog', parseInt(cur_employee_id));
    }
});