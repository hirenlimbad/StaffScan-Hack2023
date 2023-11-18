from django.shortcuts import render
from django.shortcuts import render, HttpResponse
from django.views.decorators import gzip
from django.http import StreamingHttpResponse, JsonResponse
from django.db import connection
import mysql.connector
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.template import loader
from django.middleware.csrf import get_token
from django.http import HttpResponseRedirect
from django.contrib import messages
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials, db
from django.shortcuts import render, redirect
from .forms import EmployeeLoginForm
import mysql.connector
from django.contrib.auth import authenticate, login
from django.utils import timezone
from datetime import date
import firebase_admin
from firebase_admin import credentials, db
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import csv
from django.db import connection as conn
from datetime import timedelta, datetime, date

# Initialize Firebase credentials (you've already provided this)
cred = credentials.Certificate("hackathon2023-4c407-firebase-adminsdk-xqeff-f482eeb1f8.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://hackathon2023-4c407-default-rtdb.firebaseio.com'
})


def admin_login(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            query = "SELECT * FROM Employee WHERE EmailID = %s AND password = %s"
            cursor = conn.cursor()
            cursor.execute(query, (email, password))
            user = cursor.fetchone()


            if user:
                employee_id = user[0]
                print(employee_id)
                request.session['employee_id'] = employee_id
                return redirect('employee_dashboard')
            else:
                messages.error(request, 'Invalid admin credentials. Please try again.')
    else:
        form = EmployeeLoginForm()
    return render(request, 'user_panel_template/employee_login.html', {'form': form})



def get_consecutive_on_time_days(employee_id, current_date):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT islate FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s AND DATE(Start_Time) = %s ORDER BY Start_Time DESC LIMIT 3",
            (employee_id, current_date),
        )
        attendance_records = cursor.fetchall()

    consecutive_on_time_days = 0
    for record in attendance_records:
        is_late = record[0]
        if is_late == 0:
            consecutive_on_time_days += 1
        else:
            break  # If there's a late record, the streak is broken

    return consecutive_on_time_days

def punch(request):
    employee_id = request.session.get('employee_id')
    current_time = timezone.now()
    current_date = date.today()

    with connection.cursor() as cursor:
        cursor.execute("SELECT AttendanceID, DATE(Start_Time), Start_Time FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s AND DATE(Start_Time) = %s AND End_Time IS NULL", (employee_id, current_date))
        existing_attendance = cursor.fetchone()

        if request.method == 'POST':
            if 'punch_in' in request.POST:
                if not existing_attendance:
                    # Fetch expected arrival time from the Employee table
                    cursor.execute("SELECT arrival_time FROM Employee WHERE EmployeeID = %s", (employee_id,))
                    arrival_time = cursor.fetchone()[0]

                    # Make expected arrival time timezone-aware
                    expected_arrival_datetime = datetime.combine(current_date, arrival_time, tzinfo=timezone.utc)

                    # Calculate if the employee is late
                    late_threshold = timedelta(minutes=15)  # Adjust this threshold as needed
                    is_late = current_time > (expected_arrival_datetime + late_threshold)

                    # Punch In
                    cursor.execute("INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, Start_Time, islate) VALUES (%s, %s, %s)", (employee_id, current_time, int(is_late)))
                    connection.commit()

                    # Check consecutive on-time days
                    consecutive_on_time_days = get_consecutive_on_time_days(employee_id, current_date)
                    if consecutive_on_time_days >= 3:
                        # Increment remaining_leave by the desired amount
                        increment_leave_days = 1  # You can adjust this based on your policy
                        cursor.execute("UPDATE Employee SET remaining_leave = remaining_leave + %s WHERE EmployeeID = %s", (increment_leave_days, employee_id))
                        connection.commit()

            elif 'punch_out' in request.POST:
                if existing_attendance:
                    # Punch Out
                    cursor.execute("UPDATE EMPLOYEE_ATTENDANCE SET End_Time = %s WHERE AttendanceID = %s", (current_time, existing_attendance[0]))
                    connection.commit()

    return redirect('employee_dashboard')

def employee_dashboard(request):
    current_date = date.today()
    employee_id = request.session.get('employee_id')

    # Retrieve assigned tasks for the employee from Firebase
    assigned_tasks_ref = db.reference('tasks/' + str(employee_id))
    assigned_tasks = assigned_tasks_ref.get()

    # Retrieve leave request status from Firebase
    leave_request_status_ref = db.reference(f'leave_requests/{employee_id}/status')
    leave_request_status = leave_request_status_ref.get()

    # Retrieve leave requests from Firebase
    leave_requests_ref = db.reference(f'leave_requests/{employee_id}')
    leave_requests = leave_requests_ref.get()

    # Ensure the assigned tasks exist and convert them to a list
    if assigned_tasks is not None:
        assigned_tasks = list(assigned_tasks.values())
    else:
        assigned_tasks = []

    # Initialize other variables with default values
    punch_in_count = 0
    punch_out_count = 0
    employee_name = ""

    with connection.cursor() as cursor:
        # Check if the employee has punched in on the current date
        cursor.execute("SELECT COUNT(*) FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s AND DATE(Start_Time) = %s", (employee_id, current_date))
        result = cursor.fetchone()
        if result:
            punch_in_count = result[0]

        # Check if the employee has punched out on the current date
        cursor.execute("SELECT COUNT(*) FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s AND DATE(End_Time) = %s", (employee_id, current_date))
        result = cursor.fetchone()
        if result:
            punch_out_count = result[0]

        cursor.execute("SELECT Name FROM Employee WHERE EmployeeID = %s", (employee_id,))
        result = cursor.fetchone()
        if result:
            employee_name = result[0]


        cursor.execute("SELECT admin_id FROM Employee WHERE EmployeeID = %s", (employee_id,))
        admin_id = cursor.fetchone()[0]
    return render(request, 'user_panel_template/employee_dashboard.html', {
        'punch_in_count': punch_in_count,
        'punch_out_count': punch_out_count,
        'assigned_tasks': assigned_tasks,
        'employee_name': employee_name,
        'leave_request_status': leave_request_status,
        'leave_requests': leave_requests,
        'admin_id': admin_id
    })



def edit_employee_data(request):
    if request.method == 'POST':
        try:
            # Get the data from the form
            name = request.POST['name']
            mobile = request.POST['mobile_number']
            email = request.POST['email']
            education = request.POST['education']
            position = request.POST['position']
            new_password = request.POST['new_password']  # New password field
            employee_id = request.session.get('employee_id')

            with conn.cursor() as cursor:
                # Define the SQL UPDATE statement
                update_query = "UPDATE Employee SET Name = %s, MobileNumber = %s, EmailID = %s, education = %s, position = %s, password = %s WHERE EmployeeID = %s"
                values = (name, mobile, email, education, position, new_password, employee_id)  # Include new password

                # Execute the UPDATE statement with the values
                cursor.execute(update_query, values)

                # Commit the changes to the database
                conn.commit()


            return redirect('employee_dashboard')

        except Exception as e:
            return HttpResponse(f"Error: {e}")

    # Retrieve the existing employee data for pre-filling the form
    existing_employee = get_existing_employee_data(request.session.get('employee_id'))

    # Handle GET request or render the update form with pre-filled data
    return render(request, 'user_panel_template/edit_employee_data.html', {'existing_employee': existing_employee})


def get_existing_employee_data(employee_id):
    try:
        conn = mysql.connector.connect(
            host = "hiren88.mysql.pythonanywhere-services.com", # databases.000webhost.com
            user="hiren88",
            password="ipassword",
            database="hiren88$hackathon")

        cursor = conn.cursor(dictionary=True)

        # Retrieve the existing employee data based on the employee ID
        query = "SELECT Name, MobileNumber, EmailID, education, position, salary FROM Employee WHERE EmployeeID = %s"
        cursor.execute(query, (employee_id,))

        existing_employee = cursor.fetchone()
        return existing_employee

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None




@csrf_exempt
def leave_request(request):
    remaining_leave = -1

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')

        # Create a reference to your Firebase database node where you want to store leave requests
        employee_id = request.session.get('employee_id')
        ref = db.reference(f'leave_requests/{employee_id}')

        with connection.cursor() as cursor:
            cursor.execute("SELECT admin_id FROM Employee WHERE EmployeeID = %s", (employee_id,))
            result = cursor.fetchone()
            if result:
                admin_id = result[0]
                
        ref.set({
            'start_date': start_date,
            'end_date': end_date,
            'description': description,
            'admin_id': admin_id,
        })

        return redirect('employee_dashboard')

    # Retrieve the remaining leave data from the MySQL database
    try:
        employee_id = request.session.get('employee_id')
        conn = mysql.connector.connect(
            host="localhost",
            user="unknown",
            password="password",
            database="hackathon"
        )

        cursor = conn.cursor(dictionary=True)

        query = "SELECT remaining_leave FROM Employee WHERE EmployeeID = %s"
        cursor.execute(query, (employee_id,))
        leaves = cursor.fetchone()

        if leaves:
            remaining_leave = leaves['remaining_leave']
            print(remaining_leave)

    except Exception as e:
        print(f"Error: {e}")

    return render(request, 'user_panel_template/ask_leave.html', {'remaining_leave': remaining_leave})




def download_attendance(request):
    # Get the employee ID from the session
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return HttpResponse("Employee ID not found in session")

    # Query the database to retrieve attendance data
    with connection.cursor() as cursor:
        cursor.execute("SELECT Start_Time, End_Time, leave_start, leave_end FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s", (employee_id,))
        attendance_data = cursor.fetchall()

    if not attendance_data:
        return HttpResponse("No attendance data found for this employee")

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="employee_attendance.csv"'

    # Create a CSV writer and write the header row
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Start Time', 'End Time', 'Leave Start', 'Leave End', 'Status'])

    # Write the attendance data to the CSV file, indicating "onleave" if applicable
    for row in attendance_data:
        start_time, end_time, leave_start, leave_end = row
        status = "onleave" if leave_start and leave_end else ""
        csv_writer.writerow([start_time, end_time, leave_start, leave_end, status])

    return response