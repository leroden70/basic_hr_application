from dataclasses import dataclass, field
from email.policy import default

from PostgresConnector import PostgresConnector, EmployeePostgresConnector
from re import sub as re_sub

@dataclass
class CompanyData:
    __db_connector: EmployeePostgresConnector
    _employees_list: list(dict()) = field(default_factory=list, hash=False)
    _jobs_list: list(dict()) = field(default_factory=list, hash=False)
    _departments_list: list(dict()) = field(default_factory=list, hash=False)
    _absence_types: list(dict()) = field(default_factory=list, hash=False)

    '''
    def __init__(self, db_connector:EmployeePostgresConnector):
        self._employees_list:list(dict()) = self.get_employees_list(db_connector)
        self._jobs_list: list(dict()) = self.get_jobs_list(db_connector)
        self._departments_list: list(dict()) = self.get_departments_list(db_connector)
        self._absence_types:list(dict()) = self.get_absence_types(db_connector)
    '''
    def __post_init__(self):
        self.update()

    @staticmethod
    def get_employees_list(db_connector: EmployeePostgresConnector)->list(dict()):
        return db_connector.get_employees()

    @staticmethod
    def get_jobs_list(db_connector: EmployeePostgresConnector)->list(dict()):
        return db_connector.get_job_types()

    @staticmethod
    def get_departments_list(db_connector:EmployeePostgresConnector)->list(dict()):
        return db_connector.get_departments()

    @staticmethod
    def get_absence_types(db_connector:EmployeePostgresConnector)->list(dict()):
        return db_connector.get_absence_types()

    def update(self):
        self._employees_list:list(dict()) = self.get_employees_list(self.__db_connector)
        self._jobs_list: list(dict()) = self.get_jobs_list(self.__db_connector)
        self._departments_list: list(dict()) = self.get_departments_list(self.__db_connector)
        self._absence_types:list(dict()) = self.get_absence_types(self.__db_connector)

    @property
    def employees_list(self)->list(dict()):
        return self._employees_list

    @property
    def jobs_list(self)->list(dict()):
        return self._jobs_list

    @property
    def departments_list(self)->list(dict()):
        return self._departments_list

    @property
    def absence_types(self)->list(dict()):
        return self._absence_types
    #def get_html_table(self) -> str:
    #    htmltext = """
    #    <div id='emplist'>
    #        <table class="table-clickable" id="emp_table">
    #            <thead>
    #                <tr>
    #                    <th>First Name</th>
    #                    <th>Last Name</th>
    #                    <th>Email</th>
    #                    <th>Phone</th>
    #                    <th>Job title</th>
    #                    <th>Department</th>
    #                    <th>City</th>
    #                    <th>Country</th>
    #                    <th>Region</th>
    #                </tr>
    #            </thead>
    #            <tbody>
    #    """
    #    for employee in self.employees_list:
    #        htmltext += """
    #                <tr id='{employee_id}' class='rw{row_type}' data-href='#'>
    #                    <td class='fn' >{first_name}</td>
    #                    <td class='ln' >{last_name}</td>
    #                    <td class='em' ><a href='mailto:{email}@mycompany.com'>{email}@mycompany.com</a></td>
    #                    <td class='pn' ><a href='tel:{phone_number_digits}'>{phone_number}</a></td>
    #                    <td class='jt' >{job_title}</td>
    #                    <td class='dn' >{department_name}</td>
    #                    <td class='ct' >{city}</td>
    #                    <td class='cn' >{country_name}</td>
    #                    <td  class='rn' >{region_name}</td>
    #                </tr>
    #        """.format(
    #            row_type=int(employee["row_num"]) % 2,
    #            employee_id=employee['employee_id'],
    #            first_name=employee['first_name'],
    #            last_name=employee['last_name'],
    #            email=(employee['email'].lower()),
    #            phone_number_digits=re_sub(r"(/|\.)", "", employee['phone_number']),
    #            phone_number=employee['phone_number'],
    #            job_title=employee['job_title'],
    #            department_name=employee['department_name'],
    #            city=employee['city'],
    #            country_name=employee['country_name'],
    #            region_name=employee['region_name']
    #        )
    #    htmltext += f"</tbody></table></div>\n"
    #    return htmltext

class Employee:
    def __init__(self, db_connector:EmployeePostgresConnector, company_data:CompanyData, employee_id:int):
        self.db_connector = db_connector
        self.company_data:CompanyData = company_data
        self.personal_data:dict() = self.fetch_personal_data(employee_id)
        self.job_history:list(dict()) = self.fetch_job_history(db_connector, employee_id)
        self.ent_holidays:list(dict()) = self.fetch_ent_holidays(db_connector, employee_id)

    def fetch_personal_data(self, employee_id:int)->dict():
        d = [c for c in self.company_data._employees_list if c["employee_id"] == employee_id][0]
        return d

    def fetch_job_history(self, db_connector: EmployeePostgresConnector, employee_id:int)->list(dict()):
        try:
            return db_connector.get_job_history(employee_id)
        except IndexError as e:
            self.job_history = []
        except Exception as e:
            print(e)
            raise Exception

    def update_employee_salary(self, db_connector: EmployeePostgresConnector, employee_id: int, salary:float) -> None:
        try:
            db_connector.update_salary(employee_id, salary)
            self.personal_data["salary"] = salary
            for idx, emp in enumerate(self.company_data.employees_list):
                if emp["employee_id"] == employee_id:
                    self.company_data.employees_list[idx]["salary"] = salary
        except Exception as e:
            print(e)
            raise Exception

    def update_employee_department(self, db_connector: EmployeePostgresConnector, employee_id: int, department_id: int) -> None:
        try:
            db_connector.update_department(employee_id, department_id)
            self.personal_data["department_id"] = department_id
            for idx, emp in enumerate(self.company_data.employees_list):
                if emp["employee_id"] == employee_id:
                    self.company_data[idx]["department_id"] = department_id
                    self.company_data[idx]["department_name"] = [d["department_name"] for d in self.company_data.departments_list if d["department_id"] == department_id][0]
        except Exception as e:
            print(e)
            raise Exception

    def get_job_data(self):
        job_data["employee_id"] = self.personal_data["employee_id"]
        job_data["first_name"] = self.personal_data["first_name"]
        job_data["last_name"] = self.personal_data["last_name"]
        job_data["job_id"] = self.personal_data["job_id"]
        job_data["job_title"] = self.personal_data["job_title"]
        return job_data

    def fetch_ent_holidays(self, db_connector: EmployeePostgresConnector, employee_id:int)->list(dict()):
        try:
            return db_connector.get_ent_holidays(employee_id)
        except IndexError as e:
            self.ent_holidays = []
        except Exception as e:
            print(e)
            raise Exception

    def update_salary_full(self,db_connector: EmployeePostgresConnector, emp_data: dict()):
        pass
        employee_data = emp_data
        cur_employee_id = int(emp_data[0])
        cur_job_id = emp_data[1]
        cur_hire_date = emp_data[2]
        cur_department_id = int(emp_data[3])
        new_job_id = emp_data[4]
        try:
            db_connector.update_salary_full(cur_employee_id, cur_job_id, cur_hire_date,
                                            cur_department_id, new_job_id)
        except Exception as e:
            raise e