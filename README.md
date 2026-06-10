# HR application

Basic HR application based on a simple public domain HR datamodel, slightly modified. 

## 🗂️ Project Structure
```
HR_Application/
│  
├── sql
│   ├── datamodel.sql
│   └── public_holidays.sql
├── static
│   ├── config
│   │   ├── config.py       # configuration
│   │   └── database.ini    # db connection info
│   ├── images              # images directory
│   │   └── ...
│   ├── js
│   │   ├── dialog.js       # javascript code for dialogs
│   │   └── page.js        # javascript code for page
│   └── styles
│       └── index.css       # css for the page
├── templates
│   ├── partials            # html templates for the various parts of the page
│   │   └── ...
│   └── index.html          # main page
├── tests                   # tests
│   └── ...
├── app.py                  # Entry point
├── Employee.py             # Company and Employee objects
├── PostgresConnector.py    # PG Connector objects
├── database.ini            # postgres connection paramaters
├── datamodel.sql           # Data model
└── README.md
```

```bash
python -m pip install -e .
python -m basic_hr_application        # run the demo
```

## 1. Employee's list

The employee's list is displayed, with a filter box and columns can be sorted

---

## 2. Details view

When you click on an employee in the list above, appears a detail view of the employee with  Employee ID,
Job, Department and Salary

### Options from the detail view : 

**actions on the details**
- `Change Job`
- `Change department`
- `Change salary`

**Informations about the employee**
- `Display management hierarchy`
- `Display subordinates`
- `View Job History`

**Various actions about the employee's absences**
- `Change entitlement to holidays`
- `Enter absence`

**General actions about the company**
- `Edit Departments` *not implemented yet* 
- `Edit Jobs` *not implemented yet*
---

## Dialogs :
### Change Job
A new job can be chosen from a drop down list. 
If the job is not changed a message is displayed.
If the job is changed, a new entry is added to the table `job_history`.

### Change Department
A new department can be chosen from a drop down list. 
If the department is not changed a message is displayed.
If the department is changed, a new entry is added to the table `job_history`.

### Change Salary
The salary entered must be numeric and the value must be between a minimum anx a maximum defined a the job level.

### Display management hierarchy
Displays the management chain above the employee.

### Display subordinates
Displays the management chain below the employee.

### View Job History
Displays all the job history since hire.

### Change entitlement to holidays
Each employee has some right to holidays. This can be registered here.
For each absence type is displayed the entitlement and the balance of absences. 

### Enter absence
For each absence an absence type can be chosen from a dropdown list, a start date and an estimated end date.
Later on the absence can be changed to set the actual end date of it.
A new absence updates the balance in the entitlement table.

![image](static/images/HR_datamodel.png?raw=true "Data Model")
