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


if __name__ == "__main__":
    app.run(debug=True)
