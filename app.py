from datetime import date
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
from config import config
from PostgresConnector import EmployeePostgresConnector
from Employee import CompanyData, Employee

app = Flask(__name__)
CORS(app)

db_connector = EmployeePostgresConnector(**config)
company_data = CompanyData(db_connector)

@app.route('/')
def show_index():
    return render_template('index.html')

@app.route('/employee_list')
def get_employee_list():
    employees_list = company_data.employees_list
    return render_template('partials/employee_list.html',
                           employees_list=employees_list)

@app.route('/details_dialog', methods=['POST'])
def get_details_dialog():
    data = request.get_json()
    employee_id = data.get('id')

    args = {}
    # Finds the corresponding employee
    current_employee = Employee(db_connector, company_data, employee_id)
    if not current_employee:
        return jsonify({"error": f"Employee with ID {employee_id} not found"}), 404
    try:
        args["image"] = current_employee.personal_data['photo']
        args["name"] = current_employee.personal_data['first_name'] + " " + current_employee.personal_data['last_name']
        args["employee_id"] = current_employee.personal_data['employee_id']
        args["job_title"] = current_employee.personal_data['job_title']
        args["department_name"] = current_employee.personal_data['department_name']
        args["salary"] = current_employee.personal_data['salary']
    except Exception as e:
        error = str(e)
        return jsonify({"error": str(e)}), 400
    return render_template('partials/details_dialog.html',
                           args=args)

@app.route('/job_dialog', methods=['GET', 'POST'])
def get_job_dialog():
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        # click on Submit (HTML form data)
        employee_id = request.form.get('employee_id')
        is_submit = request.form.get('action_button') == 'job_submit_button'
        current_selection = request.form.get('user_choice', '')
    else:
        # not HTMX, initial call
        data = request.get_json() or {}
        employee_id = data.get('id')
        is_submit = data.get('action_button') == 'job_submit_button'
        current_selection = data.get('user_choice', '')

    err_msg = ""
    emp = None
    jobs_list = []

    if not employee_id:
        err_msg = "ID de l'employé manquant."
    else:
        try:
            employee_id = int(employee_id)
            current_employee = Employee(db_connector, company_data, employee_id)

            """
            if not current_employee:
                err_msg = f"Employé avec l'ID {employee_id} introuvable."
            else:
                # run save if button clicked
                if is_submit:
                    print(f"Sauvegarde en BDD pour l'employé {employee_id} -> {current_selection}")
                    # Insérez votre ligne de sauvegarde de base de données ici

                # load data for html render
            """
            emp = current_employee.personal_data
            jobs_list = company_data.jobs_list

        except ValueError:
            err_msg = f"L'ID doit être un nombre entier."
        except Exception as e:
            err_msg = f"Erreur système : {str(e)}"

    # after processing submit
    if is_submit and not err_msg:  # Si c'est une soumission réussie
        response = make_response(
            render_template('partials/job_dialog.html',
                            emp=emp,
                            jobs_list=jobs_list,
                            err_msg=err_msg)
        )
        response.headers['HX-Trigger'] = 'jobSubmitted'  # Déclenche un événement JavaScript
        return response

    # For other cases (initial display or error)
    return render_template('partials/job_dialog.html',
                           emp=emp,
                           jobs_list=jobs_list,
                           err_msg=err_msg)

@app.route('/update_job', methods=['POST'])
def update_job():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400

    try:
        employee_id = int(data.get('id')[0])
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    current_employee = Employee(db_connector, company_data, employee_id)
    if not current_employee:
        return jsonify({"error": f"Employee with ID {employee_id} not found"}), 404

    cur_employee_id = int(data["id"][0])
    cur_job = data["id"][1]
    new_job = data["id"][4]
    try:
        if cur_job == new_job:
            err_msg = "You haven't changed the job."
            info_msg = ""
        else:
            current_employee.update_job_full(data["id"])
            company_data.update()
            current_employee.update(company_data)
            err_msg = ""
            info_msg = "Employee job has been changed"
    except Exception as e:
        err_msg = f"{str(e)}"
        info_msg = ""
    emp = current_employee.personal_data
    jobs_list = company_data.jobs_list
    return render_template('partials/job_dialog.html',
                           emp=emp,
                           jobs_list=jobs_list,
                           err_msg=err_msg,
                           info_msg=info_msg)

@app.route('/department_dialog', methods=['GET', 'POST'])
def get_department_dialog():
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        # click on Submit (HTML form data)
        employee_id = request.form.get('employee_id')
        is_submit = request.form.get('action_button') == 'job_submit_button'
        current_selection = request.form.get('user_choice', '')
    else:
        # not HTMX, initial call
        data = request.get_json() or {}
        employee_id = data.get('id')
        is_submit = data.get('action_button') == 'job_submit_button'
        current_selection = data.get('user_choice', '')

    err_msg = ""
    emp = None
    departments_list = []

    if not employee_id:
        err_msg = "ID de l'employé manquant."
    else:
        try:
            employee_id = int(employee_id)
            current_employee = Employee(db_connector, company_data, employee_id)
            emp = current_employee.personal_data
            departments_list = company_data.departments_list
        except ValueError:
            err_msg = f"L'ID doit être un nombre entier."
        except Exception as e:
            err_msg = f"Erreur système : {str(e)}"

    # after processing submit
    if is_submit and not err_msg:  # Si c'est une soumission réussie
        response = make_response(
            render_template('partials/department_dialog.html',
                            emp=emp,
                            depts_list=departments_list,
                            err_msg=err_msg)
        )
        response.headers['HX-Trigger'] = 'jobSubmitted'  # Déclenche un événement JavaScript
        return response

    # For other cases (initial display or error)
    return render_template('partials/department_dialog.html',
                           emp=emp,
                           depts_list=departments_list,
                           err_msg=err_msg)

@app.route('/update_department', methods=['POST'])
def update_department():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
    try:
        employee_id = int(data.get('id')[0])
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    # click on Submit (HTML form data)
    employee = Employee(db_connector, company_data, employee_id)
    employee.update_department_full(data["id"])
    company_data.update()

@app.route('/salary_dialog', methods=['POST'])
def get_salary_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400

    try:
        employee_id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    current_employee = Employee(db_connector, company_data, employee_id)
    if not current_employee:
        return jsonify({"error": f"Employee with ID {employee_id} not found"}), 404

    try:
        emp = current_employee.personal_data
        jobs_list = company_data.jobs_list
        job = [j for j in jobs_list if j["job_id"] == emp["job_id"]][0]
        err_msg = ""
        info_msg = ""
        return render_template('partials/salary_dialog.html',
                               emp=emp,
                               min_salary=job["min_salary"],
                               max_salary=job["max_salary"],
                               err_msg=err_msg,
                               info_msg=info_msg)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/update_salary', methods=['POST'])
def update_salary_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400

    try:
        employee_id = int(data.get('id')[0])
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    current_employee = Employee(db_connector, company_data, employee_id)
    if not current_employee:
        return jsonify({"error": f"Employee with ID {employee_id} not found"}), 404

    # try:
    cur_min_salary = float(data["id"][1]);
    cur_max_salary = float(data["id"][2]);
    cur_salary = float(data["id"][3]);
    try:
        new_salary = float(data["id"][4])
        if new_salary == cur_salary:
            err_msg = "You haven't changed the salary."
            info_msg = ""
        elif not cur_min_salary <= new_salary <= cur_max_salary:
            err_msg = f"The new salary must be between min {cur_min_salary} and max {cur_max_salary}."
            info_msg = ""
        else:
            current_employee.update_salary_full(new_salary)
            company_data.update()
            current_employee.update(company_data)
            err_msg = ""
            info_msg = "The salary has been changed."
    except ValueError as e:
        err_msg = f"The salary is not a number. {e}"
        info_msg = ""
    except Exception as e:
        err_msg = f"{e}"
        info_msg = ""
    emp = current_employee.personal_data
    return render_template('partials/salary_dialog.html',
                           emp=emp,
                           min_salary=cur_min_salary,
                           max_salary=cur_max_salary,
                           err_msg=err_msg,
                           info_msg=info_msg)
# except Exception as e:
    #     return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/hierarchy_dialog', methods=['POST'])
def get_hierarchy_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
    try:
        employee_id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    employees_list = company_data.employees_list

    emp_id = data.get('id')
    for empl in employees_list:
        if empl["employee_id"] == emp_id:
            htmltext = "<ul id='myUL'>"
            htmltext += print_employee(employees_list, empl, "up")
            htmltext += "</ul>"
            break
    try:
        return render_template('partials/hierarchy_dialog.html',
                               htmltext=htmltext)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/subalterns_dialog', methods=['POST'])
def get_subalterns_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
    try:
        employee_id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    employees_list = company_data.employees_list

    for empl in employees_list:
        if empl["employee_id"] == employee_id:
            htmltext = "<ul id='myUL'>"
            htmltext += print_employee(employees_list, empl, "down")
            htmltext += "</ul>"
            break
    try:
        return render_template('partials/subalterns_dialog.html',
                               htmltext=htmltext)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/entholidays_dialog', methods=['POST'])
def get_entholidays_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
    try:
        employee_id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400


    current_employee = Employee(db_connector, company_data, employee_id)
    name = f"{current_employee.personal_data['first_name']} {current_employee.personal_data['last_name']}"
    holidays_list = current_employee.ent_holidays
    legal_years_list = set([hl['legal_year'] for hl in holidays_list])
    current_year = date.today().year
    legal_year = current_year
    try:
        return render_template('partials/entholidays_dialog.html',
                               name=name,
                               employee_id=employee_id,
                               holidays_list=holidays_list,
                               legal_years_list=legal_years_list,
                               current_year=current_year,
                               legal_year=legal_year)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/holidays_dialog', methods=['POST'])
def get_holidays_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
    try:
        employee_id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    current_employee = Employee(db_connector, company_data, employee_id)
    name = f"{current_employee.personal_data['first_name']} {current_employee.personal_data['last_name']}"
    holidays_list = current_employee.act_holidays
    legal_years_list = set([hl['absence_year'] for hl in holidays_list])
    current_year = date.today().year
    legal_year = current_year
    try:
        return render_template('partials/holidays_dialog.html',
                               name=name,
                               employee_id=employee_id,
                               holidays_list=holidays_list,
                               legal_years_list=legal_years_list,
                               current_year=current_year,
                               legal_year=legal_year)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/job_history_dialog', methods=['POST'])
def get_job_history_dialog():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "Employee ID is required"}), 400
    try:
        employee_id = int(data.get('id'))
    except ValueError:
        return jsonify({"error": "Employee ID must be an integer"}), 400

    current_employee = Employee(db_connector, company_data, employee_id)
    job_history = [jh for jh in current_employee.job_history]
    name = f"{current_employee.personal_data['first_name']} {current_employee.personal_data['last_name']}"
    try:
        return render_template('partials/job_history_dialog.html',
                               name=name,
                               job_history=job_history, employee_id=employee_id)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/all_departments_dialog', methods=['POST'])
def get_all_departments_dialog():
    department = {}
    data = request.get_json()
    departments_list = company_data.departments_list
    if not data or 'id' not in data or data.get('id') == 0:
        department["department_id"] = min([d["department_id"] for d in departments_list])
    else:
        department["department_id"] = data.get('id')
    department["department_name"] = \
        [d["department_name"] for d in departments_list
         if d["department_id"] == department["department_id"]][0]
    department["manager_name"] = \
        [d["manager_name"] for d in departments_list
         if d["department_id"] == department["department_id"]][0]

    try:
        return render_template('partials/all_departments_dialog.html',
                               departments_list=departments_list,
                               department=department)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500

@app.route('/all_jobs_dialog', methods=['POST'])
def get_all_jobs_dialog():
    job = {}
    data = request.get_json()
    jobs_list = company_data.jobs_list
    if not data or 'id' not in data or data.get('id') == 0:
        job["job_id"] = min([j["job_id"] for j in jobs_list])
    else:
        job["job_id"] = data.get('id')
    job["job_title"] = [j["job_title"] for j in jobs_list
                        if j["job_id"] == job["job_id"]][0]
    job["min_salary"] = [j["min_salary"] for j in jobs_list
                         if j["job_id"] == job["job_id"]][0]
    job["max_salary"] = [j["max_salary"] for j in jobs_list
                         if j["job_id"] == job["job_id"]][0]

    try:
        return render_template('partials/all_jobs_dialog.html',
                               jobs_list=jobs_list,
                               job=job)
    except Exception as e:
        return jsonify({"error": f"Error fetching employee data: {str(e)}"}), 500


def print_employee(employees, employee, direction="down", level=0):
    textreturn = ""
    if (direction == "down"):
        subemp = [sub_employee for sub_employee in employees
                  if sub_employee["manager_id"] == employee["employee_id"]]
    else:
        subemp = [sub_employee for sub_employee in employees
                  if sub_employee["employee_id"] == employee["manager_id"]]
    textreturn += "<li>"
    if len(subemp) != 0:
        textreturn += "<span class='caret'>"
        textreturn += "</span>"
    if level > 0 and direction == "up":
        textreturn += f"reports to "
    textreturn += f"<span class='listname' onclick=\"performOperation('details_dialog',{employee["employee_id"]})\">"
    textreturn += f"{employee["first_name"]} "
    textreturn += f"{employee["last_name"]}"
    textreturn += f"</span>"
    if len(subemp) != 0:
        textreturn += "<ul class='nested'>"
        for sub_employee in subemp:
            textreturn += print_employee(employees, sub_employee, direction, level + 1)
        textreturn += "</ul>"
    textreturn += "</li>"
    return textreturn

if __name__ == "__main__":
    app.run(debug=True)
