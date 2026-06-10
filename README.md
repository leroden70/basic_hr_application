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
