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
from datetime import datetime
from django.db import connection as conn
import base64

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
            return render(request, 'showEmployee.html', {'employees': employees,
                                                         'isPresent': isPresent})

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
    except:
        return redirect('login-page')
    employees = employeeManagement().showAllEmployees(admin_id)
    present = employeeManagement().isPresent()
    message = messages.get_messages(request)
    return render(request, 'showEmployee.html', {'employees': employees,
                                                 'isPresent': present,
                                                 'message' : message})

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
        # this method will return employee id, given in post method

        id = request.POST.get('employee_id')
        cursor = conn.cursor()
        cursor.execute("select * from Employee where EmployeeID = %s", (id,))
        employee = cursor.fetchone()

        # Get the data from the database query
        id = employee[0]
        name = employee[1]
        mobile = employee[2]
        email = employee[3]

        # Create a dictionary with initial data for the form
        initial_data = {
            'id': id,
            'name': name,
            'mobile_number': mobile,
            'email': email,
            # Add other fields as needed
        }

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
            return render(request, 'showEmployee.html', {'employees': employeeManagement().showAllEmployees()})

        else:
            return HttpResponse("Form is not valid")
    else:
        form = EmployeeUpdateForm()
    return render(request, 'updatedEmployee.html', {'form': form})

from django.shortcuts import render, HttpResponse, redirect
import base64

def view_employee(request, employee_id):
    try:
        admin_id = request.session['admin_id']
    except KeyError:
        return redirect('login-page')

    cursor = conn.cursor()
    cursor.execute("SELECT EmployeeID, Name, MobileNumber, EmailID, password, education, position, salary, faceImage FROM Employee WHERE EmployeeID = %s", (employee_id,))
    employee = cursor.fetchone()

    if employee:
        # Convert the faceImage blob to base64 encoding for displaying in HTML
        if employee[8]:
            employee_image_base64 = base64.b64encode(employee[8]).decode('utf-8')
            employee = employee[:8] + (employee_image_base64,)
        else:
            employee = employee[:8] + (None,)

        # Employee found, pass the data to the template for rendering
        return render(request, 'view_employee.html', {'employee': employee})
    else:
        return HttpResponse("Employee not found")


# task assingments
def assign_task(request, employee_id, employee_name):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    if request.method == 'POST':
        form = AssignTaskForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            employee_id = form.cleaned_data['employee_id']
            employee_name = form.cleaned_data['employee_name']
            task_header = form.cleaned_data['task_header']
            task_description = form.cleaned_data['task_description']
            deadline = form.cleaned_data['deadline'].strftime('%Y-%m-%d')

            employee_task_id = form.cleaned_data['employee_id']

            # Push the data to Firebase with the new reference
            ref = db.reference('tasks/' + str(employee_task_id))
            ref.set({
                'employee_id': employee_id,
                'employee_name': employee_name,
                'task_header': task_header,
                'task_description': task_description,
                'deadline': deadline,
                'admin_id': admin_id,
                'status' : 'pending'
            })

            messages.success(request, 'Task assigned successfully.')
            return redirect('/showTasks.html')
    else:
        print("Employee ID from URL:", employee_id)
        print("Employee Name from URL:", employee_name)

        # Pre-fill the form with employee details.
        initial_data = {
            'employee_id': employee_id,
            'employee_name': employee_name,
        }
        form = AssignTaskForm(initial=initial_data)

    return render(request, 'assignTask.html', {'form': form})


def show_assigned_tasks(request):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')

    # Fetch tasks from Firebase
    tasks_ref = db.reference('tasks')
    tasks = tasks_ref.get()

    # Check if tasks were retrieved
    if tasks:
        try:
            task_list = [task for task in tasks.values()]
            task_list = [task for task in task_list if task['admin_id'] == admin_id]
            task_list.sort(key=lambda x: datetime.strptime(x['deadline'], '%Y-%m-%d'))
        except:
            task_list = tasks
            pass
    else:
        task_list = []

    return render(request, 'showTasks.html', {'tasks': task_list})

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

def late_employee(request):

    try:
        admin_id = request.session['admin_id']
    except:
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
            ) AS streaks) AS consecutive_late
        FROM Employee AS E
        WHERE admin_id = %s  # Add this line to filter by admin_id
        HAVING late_days > 0;
        """, [admin_id])


        # Fetch the results
        employees = dictfetchall(cursor)

    return render(request, 'late_employees.html', {'employees': employees})

# Helper function to fetch results as dictionaries
def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

import json
import mysql.connector
from django.http import JsonResponse

import mysql.connector

def apply_penalty(request, employee_id):
    try:
        admin_id = request.session['admin_id']
    except:
        return redirect('login-page')
    # Establish a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="unknown",
        password="password",
        database="hackathon"
    )
    cursor = conn.cursor()

    # Get the current salary from the database
    cursor.execute("SELECT salary FROM Employee WHERE EmployeeID = %s", (employee_id,))
    current_salary = cursor.fetchone()[0]

    # Calculate the new salary after reducing by 1000
    new_salary = current_salary - 1000

    # Update the salary in the database
    update_query = "UPDATE Employee SET salary = %s WHERE EmployeeID = %s"
    cursor.execute(update_query, (new_salary, employee_id))
    conn.commit()
    return redirect('late_employee')  # Corrected URL name