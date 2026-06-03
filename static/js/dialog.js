document.addEventListener("submit", async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    obj = Object.fromEntries(formData.entries());
    const myArray = Object.values(obj);
    if (e.target.id === "job_form") {
        cur_employee_id = myArray[0];
        cur_job_id = myArray[1];
        cur_hire_date = myArray[2];
        cur_department_id = myArray[3];
        new_job_id = myArray[4];
        arg = [cur_employee_id, cur_job_id, cur_hire_date, cur_department_id, new_job_id];

        await performOperation('update_job', arg, true);
        await performOperation('employee_list', parseInt(cur_employee_id));
        await performOperation('details_dialog', parseInt(cur_employee_id));
        //await performOperation('job_dialog', parseInt(cur_employee_id));
    } else if (e.target.id === "department_form") {
        cur_employee_id = myArray[0];
        cur_min_salary = myArray[1];
        cur_max_salary = myArray[2];
        cur_salary = myArray[3];
        new_salary = myArray[4];
        arg = [cur_employee_id, cur_min_salary, cur_max_salary, cur_salary, new_salary];

        await performOperation('update_salary', arg, true);
        await performOperation('employee_list', parseInt(cur_employee_id));
        await performOperation('details_dialog', parseInt(cur_employee_id));
        //await performOperation('salary_dialog', parseInt(cur_employee_id));
    } else if (e.target.id === "salary_form") {
        cur_employee_id = myArray[0];
        cur_min_salary = myArray[1];
        cur_max_salary = myArray[2];
        cur_salary = myArray[3];
        new_salary = myArray[4];
        arg = [cur_employee_id, cur_min_salary, cur_max_salary, cur_salary, new_salary];

        await performOperation('update_salary', arg, true);
        await performOperation('employee_list', parseInt(cur_employee_id));
        await performOperation('details_dialog', parseInt(cur_employee_id));
        //await performOperation('salary_dialog', parseInt(cur_employee_id));
    }
});

function filter_holidays() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("periods");
    filter = input.value;
    table = document.getElementById("enthol_table");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        yr = tr[i].dataset.year;  // → "1990"
        console.log(i, yr, input.value);  // ← ajoute ça
        if (yr === undefined) continue;  // ← ignore les lignes d'en-tête
        if (input.value == yr) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}