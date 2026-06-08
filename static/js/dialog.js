document.addEventListener("submit", async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    obj = Object.fromEntries(formData.entries());
    const arg = Object.values(obj);
    cur_employee_id = arg[0];
    if (e.target.id === "job_form") {
        action = 'update_job';
    } else if (e.target.id === "department_form") {
        action = 'update_department';
    } else if (e.target.id === "salary_form") {
        action = 'update_salary';
    } else if (e.target.id === "add_ent_form") {
        action = 'add_new_entholidays_dialog';
    } else if (e.target.id === "update_ent_form") {
        action = 'update_new_entholidays_dialog';
    } else if (e.target.id.match("eh_form")) {
        action = 'delete_entholidays_dialog';
    } else if (e.target.id === "add_abs_form") {
        action = 'add_new_holidays_dialog'
    } else if (e.target.id === "del_abs_form") {
        action = 'delete_holiday_dialog'
    }
    await performOperation(action, arg, true);
    await performOperation('employee_list');
    await performOperation('details_dialog', parseInt(cur_employee_id));
});

function filter_holidays() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("periods");
    filter = input.value;
    table = document.getElementById("enthol_table");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        yr = tr[i].dataset.year;  // → "1990"
        //console.log(i, yr, input.value);  // ← ajoute ça
        if (yr === undefined) continue;  // ← ignore les lignes d'en-tête
        if (input.value == yr) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}