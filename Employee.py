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

    def get_employees_list(self) -> list(dict()):
        return self.__db_connector.get_employees()

    def get_jobs_list(self) -> list(dict()):
        return self.__db_connector.get_job_types()

    def get_departments_list(self) -> list(dict()):
        return self.__db_connector.get_departments()

    def get_absence_types(self) -> list(dict()):
        return self.__db_connector.get_absence_types()

    def update(self):
        self._employees_list: list(dict()) = self.get_employees_list()
        self._jobs_list: list(dict()) = self.get_jobs_list()
        self._departments_list: list(dict()) = self.get_departments_list()
        self._absence_types: list(dict()) = self.get_absence_types()

    @property
    def employees_list(self) -> list(dict()):
        return self._employees_list

    @property
    def jobs_list(self) -> list(dict()):
        return self._jobs_list

    @property
    def departments_list(self) -> list(dict()):
        return self._departments_list

    @property
    def absence_types(self) -> list(dict()):
        return self._absence_types


class Employee:
    def __init__(self, db_connector: EmployeePostgresConnector, company_data: CompanyData, employee_id: int):
        self.__db_connector = db_connector
        self.employee_id: int = employee_id
        self.company_data: CompanyData = company_data
        self.personal_data: dict() = self.fetch_personal_data()
        self.job_history: list(dict()) = self.fetch_job_history()
        self.ent_holidays: list(dict()) = self.fetch_ent_holidays()
        self.act_holidays: list(dict()) = self.fetch_act_holidays()

    def fetch_personal_data(self) -> dict():
        d = [c for c in self.company_data._employees_list if c["employee_id"] == self.employee_id][0]
        return d

    def fetch_job_history(self) -> list(dict()):
        try:
            return self.__db_connector.get_job_history(self.employee_id)
        except IndexError as e:
            self.job_history = []
        except Exception as e:
            print(e)
            raise Exception

    def update_employee_salary(self, salary: float) -> None:
        try:
            self.__db_connector.update_salary(self.employee_id, salary)
            self.personal_data["salary"] = salary
            for idx, emp in enumerate(self.company_data.employees_list):
                if emp["employee_id"] == employee_id:
                    self.company_data.employees_list[idx]["salary"] = salary
        except Exception as e:
            print(e)
            raise Exception

    def update_employee_department(self, department_id: int) -> None:
        try:
            self.__db_connector.update_department(self.employee_id, department_id)
            self.personal_data["department_id"] = department_id
            for idx, emp in enumerate(self.company_data.employees_list):
                if emp["employee_id"] == employee_id:
                    self.company_data[idx]["department_id"] = department_id
                    self.company_data[idx]["department_name"] = \
                    [d["department_name"] for d in self.company_data.departments_list if
                     d["department_id"] == department_id][0]
        except Exception as e:
            print(e)
            raise Exception

    def get_job_data(self):
        job_data = {}
        job_data["employee_id"] = self.personal_data["employee_id"]
        job_data["first_name"] = self.personal_data["first_name"]
        job_data["last_name"] = self.personal_data["last_name"]
        job_data["job_id"] = self.personal_data["job_id"]
        job_data["job_title"] = self.personal_data["job_title"]
        return job_data

    def fetch_ent_holidays(self) -> list(dict()):
        try:
            return self.__db_connector.get_ent_holidays(self.employee_id)
        except IndexError as e:
            self.ent_holidays = []
        except Exception as e:
            print(e)
            raise Exception

    def fetch_act_holidays(self) -> list(dict()):
        try:
            return self.__db_connector.get_act_holidays(self.employee_id)
        except IndexError as e:
            self.ent_holidays = []
        except Exception as e:
            print(e)
            raise Exception

    def update_job_full(self, emp_data: list()):
        pass
        employee_data = emp_data
        cur_employee_id = int(emp_data[0])
        cur_job_id = emp_data[1]
        cur_hire_date = emp_data[2]
        cur_department_id = int(emp_data[3])
        new_job_id = emp_data[4]
        try:
            self.__db_connector.update_job_full(cur_employee_id, cur_job_id, cur_hire_date,
                                                cur_department_id, new_job_id)
        except Exception as e:
            raise e

    def update_department_full(self, emp_data: list()):
        pass
        employee_data = emp_data
        cur_employee_id = int(emp_data[0])
        cur_job_id = emp_data[1]
        cur_hire_date = emp_data[2]
        cur_department_id = int(emp_data[3])
        new_job_id = emp_data[4]
        try:
            self.__db_connector.update_department_full(cur_employee_id, cur_job_id, cur_hire_date,
                                                       cur_department_id, new_job_id)
        except Exception as e:
            raise e

    def update_salary_full(self, new_salary: float):
        try:
            self.__db_connector.update_salary_full(self.employee_id, new_salary)
        except Exception as e:
            raise e

    def update(self, company_data):
        self.company_data = company_data
        self.personal_data = self.fetch_personal_data()
        self.job_history = self.fetch_job_history()
        self.ent_holidays = self.fetch_ent_holidays()
        self.act_holidays = self.fetch_act_holidays()
