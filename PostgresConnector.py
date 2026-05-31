from datetime import date, timedelta
import psycopg2
from psycopg2 import OperationalError, Error
from psycopg2.extras import DictCursor

class PostgresConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **config):
        self.config = {
            "host": config.get("host", "localhost"),
            "database": config.get("database", ""),
            "user": config.get("user", ""),
            "password": config.get("password", ""),
            "port": config.get("port", "5432"),
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Connexion to PostgreSQL DB.
        Returns:
            bool: True if connexion succeeds, else False.
        """
        try:
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor(cursor_factory=DictCursor)
            print("Connexion to PostgreSQL succeeded.")
            return True
        except OperationalError as e:
            print(f"PostgreSQL connexion error : {e}")
            return False

    def disconnect(self):
        """
        Close connexion and cursor if exist.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("PostgreSQL disconnexion succeeded.")

    def execute_query(self, query, params=None, fetch=False, autocommit = True):
        """
        Executes SQL query.
        Args:
            query (str): SQL query to execute.
            params (tuple, optional): Parameters for the query (to avoid SQL injections).
            fetch (bool): If True, gets the query results.

        Returns:
            list: query results if  fetch=True, else None.
        """
        if not self.connection or self.connection.closed:
            print("Error : No active connexion.")
            return None

        try:
            self.cursor.execute(query, params)
            if fetch:
                result = [dict(row) for row in self.cursor.fetchall()]
                return result
            if autocommit == True:
                self.connection.commit()
            print("Query executed successfully.")
        except Error as e:
            if autocommit == True:
                self.connection.rollback()
            # print(f"Error while executing query : {e}")
            raise e

    def __enter__(self):
        """to use the class with a bloc 'with'."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the connexion after the bloc 'with'."""
        self.disconnect()

class EmployeePostgresConnector(PostgresConnector):
    #def __init__(self, **config):
        #super().__init__(self,**config)

    def get_job_types(self)->list(dict()):
        with self as connector:
            job_data = connector.execute_query("""
                SELECT j.job_id,
                       j.job_title,
                       j.min_salary,
                       j.max_salary
                FROM dbo.jobs j
            """, None, True)
        return job_data

    def get_employees(self) -> list(dict()):
        with self as connector:
            emp_names = connector.execute_query("""
                select ROW_NUMBER() OVER(ORDER BY e.employee_id ASC) AS row_num, e.first_name,
                       e.last_name,
                       e.email,
                       e.phone_number,
                       e.job_id,
                       j.job_title,
                       e.department_id,
                       d.department_name,
                       l.city,
                       l.state_province,
                       c.country_name,
                       r.region_name,
                       e.employee_id,
                       e.manager_id,
                       e.salary,
                       e.photo,
                       e.hire_date
                from dbo.employees e,
                     dbo.jobs j,
                     dbo.departments d,
                     dbo.locations l,
                     dbo.countries c,
                     dbo.regions r
                where e.job_id = j.job_id
                  and e.department_id = d.department_id
                  and d.location_id = l.location_id
                  and l.country_id = c.country_id
                  and c.region_id = r.region_id
            """, None, True)
        return emp_names

    def get_departments(self)->list(dict()):
        with self as connector:
            department_data = connector.execute_query("""
                SELECT d.department_id,
                       d.department_name,
					   e.first_name || ' ' || e.last_name as manager_name
                FROM dbo.departments d,
				     dbo.employees e
			   WHERE d.manager_id = e.employee_id
            """, None, True)
        return department_data

    def get_absence_types(self) -> list(dict()):
        with self as connector:
            absence_types_data = connector.execute_query("""
                SELECT abt.absence_type,
                       abt.absence_description
                  FROM dbo.absence_types abt
                  """, None, True)
        return absence_types_data

    def get_salary_data(self, employee_id)->dict():
        with self as connector:
            salary_data = connector.execute_query("""
                SELECT e.employee_id as employee_id,
                       e.first_name  as first_name,
                       e.last_name   as last_name,
                       e.salary      as salary,
                       j.job_title   as job_title,
                       j.min_salary  as min_salary,
                       j.max_salary  as max_salary
                  FROM dbo.employees e,
                       dbo.jobs j
                 WHERE e.job_id = j.job_id
                   AND e.employee_id = %s
            """, (employee_id,), True, True)
        return salary_data[0]

    def get_department_data(self, employee_id)->dict():
        with self as connector:
            employee_department_data = connector.execute_query("""
                SELECT e.employee_id, 
                       e.first_name, 
                       e.last_name, 
                       d.department_name, 
                       d.department_id 
                  FROM dbo.employees e, 
                       dbo.departments d 
                 WHERE e.department_id = d.department_id 
                   AND e.employee_id = %s 
            """, (employee_id,), True, True)
        return employee_department_data[0]

    def get_job_history(self, employee_id)->list(dict()):
        with self as connector:
            employee_job_data = connector.execute_query("""
                SELECT h.employee_id,
                       h.start_date,
                       h.end_date,
                       j.job_title,
                       d.department_name
                  FROM (SELECT employee_id,
                               start_date,
                               end_date,
                               job_id,
                               department_id
                          FROM dbo.job_history
                        UNION
                        (SELECT e.employee_id, 
                                COALESCE(jh1.end_date + 1, e.hire_date) AS start_date,
                                CAST('9999-12-31' AS DATE) AS end_date,
                                e.job_id,
                                e.department_id
                           FROM dbo.employees e
                         LEFT OUTER JOIN (SELECT employee_id,
                                                 MAX(end_date) AS end_date
                                            FROM dbo.job_history
                                          GROUP BY employee_id) jh1
                                      ON jh1.employee_id = e.employee_id)) h
                INNER JOIN dbo.jobs j
                        ON h.job_id = j.job_id
                INNER JOIN dbo.departments d
                        ON h.department_id = d.department_id
                 WHERE h.employee_id = %s
                ORDER BY h.start_date ASC
            """, (employee_id,), True, True)
        return employee_job_data

    def get_ent_holidays(self, employee_id) -> list(dict()):
        with self as connector:
            employee_entholidays_data = connector.execute_query("""
                SELECT u.employee_id,
                       u.legal_year,
                       u.absence_type,
                       ab.absence_description,
                       u.entitlement,
                       u.balance
                  FROM (SELECT eh1.employee_id,
                               generate_series(              
                                   EXTRACT(YEAR FROM start_date)::int       ,
                                   EXTRACT(YEAR FROM        current_date)::int
                               ) AS legal_year,
                               eh1.absence_type,
                               eh1.entitlement,
                               eh1.balance
                          FROM dbo.emp_holidays eh1
                         WHERE eh1.end_date = '9999-12-31'
                        UNION
                        SELECT eh.employee_id,
                               generate_series(
                                   EXTRACT(YEAR FROM start_date)::int,
                                   EXTRACT(YEAR FROM end_date)::int
                               ) AS legal_year,
                               eh.absence_type,
                               eh.entitlement,
                               eh.balance
                          FROM dbo.emp_holidays eh
                         WHERE eh.end_date <> '9999-12-31') u
                INNER JOIN dbo.absence_types ab
                        ON u.absence_type = ab.absence_type
                WHERE u.employee_id = %s
                ORDER BY u.legal_year, u.absence_type
            """, (employee_id,), True, True)
        return employee_entholidays_data

    def update_employee_salary(self, employee_id: int, salary: float) -> None:
        try:
            with self as connector:
                connector.execute_query("""
                    UPDATE dbo.employees
                       SET salary = %s
                     WHERE employee_id = %s
                """, (salary, employee_id))
        except Exception as e:
            raise Exception(f"The salary could not be updated for employee {employee_id}. Error: {e}")

    def update_employee_department(self, employee_id: int, department_id: int) -> None:
        try:
            with self as connector:
                connector.execute_query("""
                    UPDATE dbo.employees
                       SET department_id = %s
                     WHERE employee_id = %s
                """, (department_id, employee_id))
        except Exception as e:
            raise Exception(f"The department could not be updated for employee {employee_id}. Error: {e}")

    def update_job_full(self, cur_employee_id: int,cur_job_id: str,
                           cur_hire_date: str,cur_department_id: int,new_job_id: str):
        self.connect()
        # 1. update job_history :
        #       select last record from job_history where employee_id = cur_employee_id
        #           retrieve hist_start_date = start_date, hist_end_date = end_date
        #       if no history
        #           create record with
        #               employee_id = cur_employee_id,
        #               start_date = cur_hire_date,
        #               end_date = today - 1,
        #               job_id = cur_job_id,
        #               department_id = cur_department_id
        #       else
        #           if hist_end_date = today - 1
        #               do nothing
        #           else
        #               create a record in job_history  with
        #                   employee_id = cur_employee_is
        #                   start_date = hist_end_date + 1,
        #                   end_date = today - 1,
        #                   job_id = cur_job_id
        #                   department_id = cur_department_id
        # 2. update employee.job_id
        #       set job_id = new_job_id
        #       where employee_id = cur_employee_id
        try:
            employee_job_data = self.execute_query("""
                SELECT jh.start_date,
                       jh.end_date
                  FROM dbo.job_history jh
                 WHERE jh.employee_id = %s
                ORDER BY jh.start_date desc;
                """, (cur_employee_id,), True, False)
            if not employee_job_data:
                try:
                    self.execute_query("""
                       INSERT INTO dbo.job_history (employee_id, start_date, end_date, job_id,
                                                    department_id)
                       VALUES (%s, %s, CURRENT_DATE - 1, %s, %s);
                    """, (cur_employee_id, cur_hire_date, cur_job_id, cur_department_id)
                                       , False, False)
                except Exception as e:
                    self.connection.rollback()
                    print(f"Error executing query: {e}")
            else:
                hist_start_date = employee_job_data[0]["start_date"]
                hist_end_date = employee_job_data[0]["end_date"]
                if hist_end_date != date.today() - timedelta(days=1):
                    start_date = hist_end_date + timedelta(days=1)
                    try:
                        self.execute_query("""
                            INSERT INTO dbo.job_history (
                                employee_id, start_date, end_date, job_id, department_id
                            ) VALUES (
                                %s, %s , CURRENT_DATE - 1, %s, %s
                            );
                        """, (cur_employee_id, start_date, cur_job_id, cur_department_id),
                                           False, False)
                    except Exception as e:
                        self.connection.rollback()
                        print(f"Error executing query: {e}")
            try:
                self.execute_query(f"""
                    UPDATE dbo.employees
                       SET job_id = %s
                     WHERE employee_id = %s
                 """, (new_job_id, cur_employee_id), False, False)
            except Exception as e:
                self.connection.rollback()
                print (f"Error executing query: {e}")
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing query: {e}")
        self.connection.commit()
        self.disconnect()

    def update_department_full(self, cur_employee_id: int,cur_job_id: str,
                           cur_hire_date: str,cur_department_id: int,new_department_id: str):
        self.connect()
        try:
            employee_job_data = self.execute_query("""
                SELECT jh.start_date,
                       jh.end_date
                  FROM dbo.job_history jh
                 WHERE jh.employee_id = %s
                ORDER BY jh.start_date desc;
                """, (cur_employee_id,), True, False)
            if not employee_job_data:
                try:
                    self.execute_query("""
                       INSERT INTO dbo.job_history (employee_id, start_date, end_date, job_id,
                                                    department_id)
                       VALUES (%s, %s, CURRENT_DATE - 1, %s, %s);
                    """, (cur_employee_id, cur_hire_date, cur_job_id, cur_department_id)
                                       , False, False)
                except Exception as e:
                    self.connection.rollback()
                    print(f"Error executing query: {e}")
            else:
                hist_start_date = employee_job_data[0]["start_date"]
                hist_end_date = employee_job_data[0]["end_date"]
                if hist_end_date != date.today() - timedelta(days=1):
                    start_date = hist_end_date + timedelta(days=1)
                    try:
                        self.execute_query("""
                            INSERT INTO dbo.job_history (
                                employee_id, start_date, end_date, job_id, department_id
                            ) VALUES (
                                %s, %s , CURRENT_DATE - 1, %s, %s
                            );
                        """, (cur_employee_id, start_date, cur_job_id, cur_department_id),
                                           False, False)
                    except Exception as e:
                        self.connection.rollback()
                        print(f"Error executing query: {e}")
            try:
                self.execute_query(f"""
                    UPDATE dbo.employees
                       SET department_id = %s
                     WHERE employee_id = %s
                 """, (new_department_id, cur_employee_id), False, False)
            except Exception as e:
                self.connection.rollback()
                print (f"Error executing query: {e}")
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing query: {e}")
        self.connection.commit()
        self.disconnect()

