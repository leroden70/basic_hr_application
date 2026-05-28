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
    data = request.get_json()
    employee_id = data.get('id')
    if not data or 'id' not in data:
        print("not data or 'id' not in data")
    if not(data.get('id')):
        print("not(data.get('id'))")

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
    employee_id = None
    is_submit = False
    current_selection = ""

    # DÉTECTION ULTRA-FIABLE : Est-ce que la requête vient de HTMX ?
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        # C'est le clic sur le bouton Submit (Données du Formulaire HTML)
        employee_id = request.form.get('employee_id')
        is_submit = request.form.get('action_button') == 'job_submit_button'
        current_selection = request.form.get('user_choice', '')
    else:
        # Ce n'est pas HTMX, c'est l'appel initial en JSON pour ouvrir la modale
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

            if not current_employee:
                err_msg = f"Employé avec l'ID {employee_id} introuvable."
            else:
                # Si le bouton submit a été cliqué, on exécute la sauvegarde
                if is_submit:
                    print(f"Sauvegarde en BDD pour l'employé {employee_id} -> {current_selection}")
                    # Insérez votre ligne de sauvegarde de base de données ici

                # On charge systématiquement les données pour le rendu HTML
                emp = current_employee.personal_data
                jobs_list = company_data.jobs_list

        except ValueError:
            err_msg = f"L'ID doit être un nombre entier."
        except Exception as e:
            err_msg = f"Erreur système : {str(e)}"

    # Après traitement de la soumission
    if is_submit and not err_msg:  # Si c'est une soumission réussie
        response = make_response(
            render_template('partials/job_dialog.html',
                           emp=emp,
                           jobs_list=jobs_list,
                           err_msg=err_msg)
        )
        response.headers['HX-Trigger'] = 'jobSubmitted'  # Déclenche un événement JavaScript
        return response

    # Pour les autres cas (affichage initial ou erreur)
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
    employee = Employee(db_connector, company_data, employee_id)
    # employee.update_salary_full(db_connector, data.get('id'))
    # company_data.update()
    jobs_list = company_data.jobs_list
    err_msg = ""
    return render_template('partials/job_dialog.html',
                           emp=employee_id,
                           jobs_list=jobs_list,
                           err_msg=err_msg)

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

    emp_id = data.get('id')
    for empl in employees_list:
        if empl["employee_id"] == emp_id:
            htmltext = "<ul id='myUL'>"
            htmltext += print_employee(employees_list, empl, "down")
            htmltext += "</ul>"
            break
    try:
        return render_template('partials/subalterns_dialog.html',
                               htmltext=htmltext)
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
