def delete_holiday(self, employee_id: int, absence_type: str,
                   start_date: date, country_id: str):
    sql = [""] * 3
    values = [""] * 3
    workdays = self.workdays(start_date, end_date, country_id)
    bankholidays = self.bankholidays(start_date, end_date, country_id)
    sql[0] = """
        DELETE FROM absences 
         WHERE employee_id = %s
           AND absence_type = %s
           AND start_date = %s
        RETURNING employee_id, estimated_end_date, end_date
    """
    values[0] = (employee_id, absence_type, start_date)
    sql[1] = """
        UPDATE emp_holidays
           set balance = balance + %s 
         WHERE employee_id = %s
           AND absence_type = %s
           AND %s BETWEEN start_date AND end_date
        RETURNING employee_id 
    """
    values[1] = (workdays, employee_id, absence_type, start_date)
    sql[2] = """
        UPDATE emp_holidays
           set balance = balance + %s 
         WHERE employee_id = %s
           AND absence_type = 'PUBL'
           AND %s BETWEEN start_date AND end_date
        RETURNING employee_id 
    """
    values[2] = (bankholidays, employee_id, absence_type, start_date)
    self.connection = psycopg2.connect(**self.config)
    try:
        with (self.connection.cursor(cursor_factory=DictCursor) as cursor0,
              self.connection.cursor(cursor_factory=DictCursor) as cursor1,
              self.connection.cursor(cursor_factory=DictCursor) as cursor2):
            cursor0.execute(sql[0], values[0])
            employee_hol_data = [dict(row) for row in cursor0.fetchall()]
            if not employee_hol_data:
                raise Exception(f"Cannot delete this absence")
            cursor1.execute(sql[1], values[1])
            employee_enthol_data = [dict(row) for row in cursor1.fetchall()]
            if not employee_enthol_data:
                raise Exception(f"Cannot update the holidays entitlement balance")
            cursor2.execute(sql[2], values[2])
            employee_enthol_data = [dict(row) for row in cursor2.fetchall()]
            if not employee_enthol_data:
                raise Exception(f"Cannot update the holidays entitlement balance")
    except Exception as e:
        self.connection.rollback()
        print(f"Error executing query: {e}")
        raise e
    self.connection.commit()
    self.disconnect()
