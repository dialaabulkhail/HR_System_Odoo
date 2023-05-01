

from flask import Flask, render_template, request
import xmlrpc.client
from datetime import datetime
import os


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)

url = 'http://arab-engineering-company.odoo.com'
db = 'arab-engineering-company'
username = 'haymouni@arab-engco.com'
password = 'Arab@2020'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    employee_id = request.form['employee_id']
    current_time = request.form['current_time']
    current_date = request.form['current_date']
    current_location = request.form['current_location']
    current_datetime = current_date + ' ' + current_time

    # Convert the current_time string to a datetime object
    check_in = datetime.strptime(current_datetime, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

    # Check if the employee has already checked in today
    today = datetime.today().strftime('%Y-%m-%d')
    attendance_ids = models.execute_kw(db, uid, password, 'hr.attendance', 'search', [[
        ('employee_id', '=', int(employee_id)),
        ('check_in', '>=', today),
        ('check_out', '=', False)
    ]])

    if attendance_ids:
        # Update the existing attendance record with the check_out value
        models.execute_kw(db, uid, password, 'hr.attendance', 'write', [[attendance_ids[0]], {
            'check_out': check_in,
            'x_studio_check_out_location': current_location
        }])
        message = 'Attendance checked out successfully.'
        return message
      
    else:
        # Create a new record in the hr.attendance model
        attendance_vals = {
            'employee_id': int(employee_id),
            'check_in': check_in,
            'x_studio_location': current_location,
        }
        attendance_id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [attendance_vals])
        message = 'Attendance checked in successfully.'

    return message


# if __name__ == '__main__':
#     app.run(debug=True)

app.run(host='0.0.0.0', port=8080)
