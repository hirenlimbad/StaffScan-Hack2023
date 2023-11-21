from django.shortcuts import render, HttpResponse
from .forms import EmployeeForm
from .employeeManagement import employeeManagement
from .employeeUpdateForm import EmployeeUpdateForm
from .models import Frame
from django.views.decorators import gzip
from django.http import StreamingHttpResponse, JsonResponse
from django.db import connection
import mysql.connector
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.template import loader
from django.middleware.csrf import get_token
from .forms import AssignTaskForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from firebase_admin import db
from .models import Employee
import firebase_admin
from firebase_admin import credentials, db
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date
from django.db import connection as conn
from django.db import transaction
import base64
import uuid  

# from .AttendanceMechanism import AttendanceMechanism

# cred = credentials.Certificate("hackathon2023-4c407-firebase-adminsdk-xqeff-f482eeb1f8.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://hackathon2023-4c407-default-rtdb.firebaseio.com'
# })

# Create your views here.
def index(request):
    return render(request,'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = employeeManagement().checkCredentials(username, password)
        if (user) != None:
            request.session['admin_id'] = user
            employees = employeeManagement().showAllEmployees(user)
            isPresent = employeeManagement().isPresent()
            currunt_time = datetime.now()
            return render(request, 'showEmployee.html', {'employees': employees,
                                                         'isPresent': isPresent,
                                                         'current_time': currunt_time})

        text = {"error_message": "Sorry! incorrect user name or password."}
        return render(request, 'LoginPage.html', text)
    else:
        return render(request, 'LoginPage.html')

def add_employee(request):

    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            admin_id = request.session['admin_id']
            employeeManagement().saveEmployeeForm(form, admin_id)
            admin_id = request.session['admin_id']
            employees = employeeManagement().showAllEmployees(admin_id)
            isPresent = employeeManagement().isPresent()
            return render(request, 'showEmployee.html', {'employees': employees,
                                                         'isPresent': isPresent})

        else:
            return HttpResponse("Form is not valid")
    else:
        form = EmployeeForm()
    return render(request, 'addEmployee.html', {'form': form})

def employee_list(request):
    try:
        admin_id = request.session['admin_id']
        current_time = datetime.now()
        print("time is: ",current_time)
    except:
        return redirect('login-page')
    employees = employeeManagement().showAllEmployees(admin_id)
    present = employeeManagement().isPresent()
    message = messages.get_messages(request)

    return render(request, 'showEmployee.html', {'employees': employees,
                                                 'isPresent': present,
                                                 'message' : message,
                                                 'current_time': current_time})

def get_latest_employee_data(request):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    employees = employeeManagement().showAllEmployees(admin_id)
    present = employeeManagement().isPresent()

    # Render the employee data in a template and return it as HTML
    html = render(request, 'showEmployeePartial.html', {'employees': employees, 'isPresent': present})

    # Return the HTML response
    return JsonResponse({'html': html.content.decode('utf-8')})

def edit_employee(request):

    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    form1 = EmployeeUpdateForm()

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Employee WHERE EmployeeID = %s", (employee_id,))
        employee = cursor.fetchone()
        if employee:
            # Extracting data from the database query
            id, name, mobile, email, password ,education, position, salary, face_image, *extra_values = employee
            initial_data = {
                'id': id,
                'name': name,
                'mobile_number': mobile,
                'email': email,
                'password': password,
                'education': education,
                'position': position,
                'salary': salary
            }

            print("password is: ", password)

            # Create the form instance with initial data
            form = EmployeeUpdateForm(initial=initial_data)

            return render(request, 'editEmployee.html', {'form': form})

def delete_employee(request):

    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    if request.method == "POST":

        employee_id = request.POST.get("employee_id")
        if employee_id:
            try:

                # Create a cursor
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM Employee WHERE EmployeeID = %s", (employee_id,))
                employee_name = cursor.fetchone()

                if employee_name:
                    # Query to delete the employee by their ID
                    cursor.execute("DELETE FROM Employee WHERE EmployeeID = %s", (employee_id,))
                    conn.commit()

                    # Optionally, you can retrieve the updated employee list and pass it to the template.
                    updated_employee_list = employee_list(request)  # You should implement this function.
                    admin_id = request.session['admin_id']
                    employees = employeeManagement().showAllEmployees(admin_id)
                    return render(request, 'showEmployee.html', {
                        'success_message': 'Employee deleted successfully.',
                        'employee_list': updated_employee_list,
                         'employees': employees
                    })
                else:
                    admin_id = request.session['admin_id']
                    employees = employeeManagement().showAllEmployees(admin_id)
                    html = {'error_message': 'Employee not found', 'employees': employees}
                    return render(request, 'showEmployee.html', html)
            except mysql.connector.Error as err:
                # Handle database errors here
                return HttpResponse(f"Database error: {err}")
        else:
            return HttpResponse("Invalid employee ID")
    else:
        return HttpResponse("Invalid request method")

def update_employee(request):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            employeeManagement().updateEmployeeForm(request)
            admin_id = request.session['admin_id']
            employees = employeeManagement().showAllEmployees(admin_id)
            present = employeeManagement().isPresent()
            return render(request, 'showEmployee.html', {'employees': employees,
                                                         'isPresent': present})

        else:
            return HttpResponse("Form is not valid")
    else:
        form = EmployeeUpdateForm()
    return HttpResponse("hmm lets debug it.")

from django.shortcuts import render, HttpResponse, redirect
import base64

def view_employee(request, employee_id):
    try:
        admin_id = request.session['admin_id']
    except KeyError:
        return redirect('login-page')

    # Fetch employee details
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EmployeeID, Name, MobileNumber, EmailID, password, education, position, salary, faceImage, penalty FROM Employee WHERE EmployeeID = %s",
            (employee_id,))
        employee = cursor.fetchone()
        penualty = employee[-1] 

        # Convert the faceImage blob to base64 encoding for displaying in HTML
        if employee and employee[8]:
            employee_image_base64 = base64.b64encode(employee[8]).decode('utf-8')
            employee = employee[:8] + (employee_image_base64,)
        else:
            employee = employee[:8] + (None,)

        # Fetch employee attendance data
        cursor.execute(
            "SELECT AttendanceID, Start_Time, End_Time, leave_start, leave_end, islate FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s",
            (employee_id,))
        rows = cursor.fetchall()

        # Convert tuples to dictionaries and format datetime objects
        attendance_data = []
        for row in rows:
            entry = {
                'AttendanceID': row[0],
                'Date': datetime.strftime(row[1], '%Y-%m-%d') if row[1] else None,
                'Start_Time': datetime.strftime(row[1], '%Y-%m-%d %H:%M:%S') if row[1] else None,
                'End_Time': datetime.strftime(row[2], '%Y-%m-%d %H:%M:%S') if row[2] else None,
                'leave_start': row[3],
                'leave_end': row[4],
                'islate': row[5]
            }
            attendance_data.append(entry)
        print(attendance_data)
    # Pass the data to the template for rendering
    return render(request, 'view_employee.html', {'employee': employee, 'attendance_data': attendance_data, 'penualty': penualty})


def assign_task(request, employee_id, employee_name):
    try:
        admin_id = request.session['admin_id']
    except KeyError:
        return redirect('login-page')

    if request.method == 'POST':
        form = AssignTaskForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            cleaned_employee_id = form.cleaned_data['employee_id']
            cleaned_employee_name = form.cleaned_data['employee_name']
            task_header = form.cleaned_data['task_header']
            task_description = form.cleaned_data['task_description']
            deadline = form.cleaned_data['deadline'].strftime('%Y-%m-%d')

            # Generate a unique identifier for the task
            task_id = str(uuid.uuid4())

            # Push the data to Firebase with the new reference
            ref = db.reference(f'tasks/{cleaned_employee_id}/{task_id}')
            ref.set({
                'employee_id': cleaned_employee_id,
                'employee_name': cleaned_employee_name,
                'task_header': task_header,
                'task_description': task_description,
                'deadline': deadline,
                'admin_id': admin_id,
                'status': 'pending'
            })

            messages.success(request, 'Task assigned successfully.')

            # Redirect to the desired URL after assigning the task
            return redirect('/showTasks.html')

        return HttpResponse("Form is not valid")
    else:
        form = AssignTaskForm()
        initial_data = {
            'employee_id': employee_id,
            'employee_name': employee_name,
        }
        form = AssignTaskForm(initial=initial_data)

    return render(request, 'assignTask.html', {'form': form})

# views.py

def show_assigned_tasks(request):
    try:
        admin_id = request.session['admin_id']
    except KeyError:
        return redirect('login-page')

    # Fetch tasks from Firebase
    tasks_ref = db.reference('tasks')
    tasks = tasks_ref.get()
    task_list = []

    if tasks:
        for employee_id, employee_tasks in tasks.items():
            if isinstance(employee_tasks, dict):
                for date, task_details in employee_tasks.items():
                    if isinstance(task_details, dict) and task_details.get('admin_id') == admin_id:
                        task_details['task_id'] = date  # Assign the task ID here
                        task_details['employee_id'] = employee_id
                        task_list.append(task_details)

    return render(request, 'showTasks.html', {'tasks': task_list})

def dismiss_task(request, employee_id, deadline, task_id):
    try:
        task_ref_path = f'tasks/{employee_id}/{task_id}'

        # Get a reference to the task node
        task_ref = db.reference(task_ref_path)

        # Check if the task exists
        if task_ref.get():
            # Remove the task from Firebase
            task_ref.delete()

            # Assuming the task dismissal is successful
            response_data = {'status': 'success'}
        else:
            # Task not found
            response_data = {'status': 'error', 'message': 'Task not found'}

    except Exception as e:
        # Handle any exceptions that might occur during the dismissal process
        response_data = {'status': 'error', 'message': str(e)}

    return JsonResponse(response_data)


# camera field goes from here.
def get_frame():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


def actual_video_feed(request):
    return render(request, 'cameraSetup.html')


def assign_leave(request):
    try:
        admin_id = request.session['admin_id']
        print(admin_id)
    except:
        return redirect('login-page')

    leave_requests_ref = db.reference('leave_requests')
    leave_requests = leave_requests_ref.order_by_child('admin_id').equal_to(admin_id).get()
    return render(request, 'assign_leave.html', {'leave_requests': leave_requests})

@csrf_exempt
def approve_leave(request, employee_id):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    if request.method == 'POST':
        if 'approve' in request.POST:
            try:
                cursor = conn.cursor()

                # Insert the approved leave request into MySQL
                insert_sql = "INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, leave_start, leave_end) VALUES (%s, %s, %s)"
                cursor.execute(insert_sql, (employee_id, request.POST['start_date'], request.POST['end_date']))
                conn.commit()

                # Update Firebase record to indicate approval
                ref = db.reference(f'leave_requests/{employee_id}')
                ref.update({'status': 'approved'})

                # Calculate the duration and decrease the remaining leave count in the Employee table
                leave_start = datetime.strptime(request.POST['start_date'], '%Y-%m-%d')
                leave_end = datetime.strptime(request.POST['end_date'], '%Y-%m-%d')
                leave_duration = (leave_end - leave_start).days

                update_sql = "UPDATE Employee SET remaining_leave = remaining_leave - %s WHERE EmployeeID = %s"
                cursor.execute(update_sql, (leave_duration, employee_id))
                conn.commit()

                return redirect('assign_leave')  # Corrected URL name

            except Exception as e:
                # Handle database or Firebase errors and log the details
                print(f"Error: {e}")
                return HttpResponse("An error occurred while processing the request.")

        elif 'decline' in request.POST:
            try:
                # Update the Firebase record to indicate decline
                ref = db.reference(f'leave_requests/{employee_id}')
                ref.update({'status': 'declined'})

                return redirect('assign_leave')  # Corrected URL name

            except Exception as e:
                # Handle Firebase errors and log the details
                print(f"Error: {e}")
                return HttpResponse("An error occurred while processing the request.")

    return HttpResponse("Invalid request")



# late employees

# def late_employee(request):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="unknown",  # Replace with your MySQL username
#         password="password",  # Replace with your MySQL password
#         database="hackathon"
#     )

#     cursor = conn.cursor()
#     query = "SELECT E.EmployeeID, E.Name, E.position, (SELECT COUNT(*) FROM EMPLOYEE_ATTENDANCE AS A WHERE A.EmployeeID = E.EmployeeID AND A.islate = 1) AS late_days FROM Employee AS E HAVING late_days > 0;"

#     cursor.execute(query)
#     late_employee_list = cursor.fetchall()

#     print(late_employee_list)
#     context = {'late_employee_list': late_employee_list}
#     return render(request, 'late_employees.html', context)
from django.shortcuts import render, redirect
from django.db import connection

def late_employee(request):
    try:
        admin_id = request.session['admin_id']
    except KeyError:
        return redirect('login-page')

    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT
            E.EmployeeID,
            E.Name,
            E.Position,
            (SELECT COUNT(*) FROM EMPLOYEE_ATTENDANCE AS A WHERE A.EmployeeID = E.EmployeeID AND A.islate = 1) AS late_days,
            (SELECT MAX(LateStreak) FROM (
                SELECT EmployeeID, islate,
                    IF(@prevEmp = A.EmployeeID, IF(A.islate = 1, @streak := @streak + 1, @streak := 0), @streak := 0) AS LateStreak,
                    @prevEmp := A.EmployeeID
                FROM EMPLOYEE_ATTENDANCE AS A
                WHERE A.EmployeeID = E.EmployeeID
                ORDER BY A.Start_Time
            ) AS streaks) AS consecutive_late,
            (SELECT MAX(Start_Time) FROM EMPLOYEE_ATTENDANCE AS A WHERE A.EmployeeID = E.EmployeeID) AS last_punch_in_time
        FROM Employee AS E
        WHERE admin_id = %s
        HAVING late_days > 0;
        """, [admin_id])

        employees = dictfetchall(cursor)

    return render(request, 'late_employees.html', {'employees': employees})

# Helper function to fetch results as dictionaries
def dictfetchall(cursor):
    desc = cursor.description
    rows = cursor.fetchall()

    if rows is not None:
        return [dict(zip([col[0] for col in desc], row)) for row in rows]
    else:
        return []


def apply_penalty(request, employee_id):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    # Establish a connection to the MySQL database
    cursor = conn.cursor()

    # Get the current salary from the database
    cursor.execute("SELECT penalty FROM Employee WHERE EmployeeID = %s", (employee_id,))
    penalty = cursor.fetchone()[0]

    # Calculate the new salary after reducing by 1000

    if penalty is not None:
        penalty = penalty + 1000
    else:
        penalty = 1000

    # Update the salary in the database
    update_query = "UPDATE Employee SET penalty = %s WHERE EmployeeID = %s"
    cursor.execute(update_query, (penalty, employee_id))
    conn.commit()

    # after applying penalty, update the late streak to 0
    update_query = "UPDATE EMPLOYEE_ATTENDANCE SET islate = 0 WHERE EmployeeID = %s"
    affected_rows = cursor.execute(update_query, (employee_id,))
    conn.commit()

    if affected_rows > 0:
        return HttpResponse("Penalty applied successfully.")
    return redirect('late_employee')

from django.db import IntegrityError

def setTimings(request):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')

    if request.method == 'POST':
        position = request.POST.get('position')
        arrival_time = request.POST.get('arrival_time')

        with connection.cursor() as cursor:
            cursor.execute("UPDATE Employee SET arrival_time = %s WHERE position = %s AND admin_id = %s", [arrival_time, position, admin_id])

    # Retrieve timings after update/insert
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT position, arrival_time FROM Employee WHERE arrival_time IS NOT NULL AND admin_id = %s", [admin_id])
        rows = cursor.fetchall()
        timings = {row[0]: row[1] for row in rows}

    return render(request, 'setTimings.html', {'timings': timings})
