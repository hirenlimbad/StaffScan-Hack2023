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
import base64
import face_recognition
from PIL import Image
import io
import cv2
import numpy as np

# Initialize Firebase credentials (you've already provided this)
cred = credentials.Certificate("hackathon2023-4c407-firebase-adminsdk-xqeff-f482eeb1f8.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://hackathon2023-4c407-default-rtdb.firebaseio.com'
})

# settings for indina time zone
import pytz
IST = pytz.timezone('Asia/Kolkata')



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
    try:
        employee_id = request.session['employee_id']
    except KeyError:
        return redirect('employee_login')

    # current_time will be in India time zone
    current_time = datetime.now(IST)
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

                    print(f"Expected arrival time: {arrival_time} and is late: ", end="")

                    # Convert arrival_time to datetime and make it timezone-aware
                    arrival_datetime = datetime.combine(current_date, arrival_time)
                    arrival_datetime_aware = IST.localize(arrival_datetime)

                    # Calculate if the employee is late
                    late_threshold = timedelta(minutes=60)  # Adjust this threshold as needed
                    is_late = current_time > (arrival_datetime_aware + late_threshold)
                    print("current time: ", current_time, is_late, (arrival_datetime_aware + late_threshold))

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

@csrf_exempt
def upload_photo(request):
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image_data')
            

        except Exception as e:
            print(e)

    return HttpResponse('Invalid request method or no image data provided.')


def image_will_upload(request):
    return render(request, 'user_panel_template/image_will_upload.html')

@csrf_exempt
def upload_image(request):
    try:
        if request.method == 'POST' and request.FILES.get('image'):
            image_file = request.FILES['image']
            image = Image.open(image_file)
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Get the employee ID from the session
            employee_id = request.session.get('employee_id')
            # get the face image from the database
            cursor = conn.cursor()
            query = "SELECT faceImage FROM Employee WHERE EmployeeID = %s"
            cursor.execute(query, (employee_id,))
            employee = cursor.fetchone()

            # Get the face encodings for the current employee
            if employee and employee[0]:
                employee_image = employee[0]
                employee_image = np.array(Image.open(io.BytesIO(employee_image)))
                employee_image = cv2.cvtColor(employee_image, cv2.COLOR_BGR2RGB)
                

                employee_face_encodings = face_recognition.face_encodings(employee_image)
                if len(employee_face_encodings) > 0:
                    employee_face_encoding = employee_face_encodings[0]

                    # Get the face encodings for the current uploaded image
                    unknown_face_encodings = face_recognition.face_encodings(image)
                    if len(unknown_face_encodings) > 0:
                        # Check if there are multiple faces in the uploaded image
                        if len(unknown_face_encodings) > 1:
                            return JsonResponse({'message': 'Multiple faces detected in the uploaded image'})
                        
                        unknown_face_encoding = unknown_face_encodings[0]
                        
                        # Compare the faces and get the distance
                        face_distance = face_recognition.face_distance([employee_face_encoding], unknown_face_encoding)
                        if face_distance < 0.5:
                            return JsonResponse({'message': 'Face matches', 'success': 'face matches'})
                        else:
                            return JsonResponse({'message': 'Face does not match'})
                    else:
                        return JsonResponse({'message': 'No face found in the uploaded image'})
                else:
                    return JsonResponse({'message': 'No face found in the employee image'})
            else:
                return JsonResponse({'message': 'No face found in the employee image'})

        return JsonResponse({'message': 'Image uploaded successfully'})
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Error uploading image'})

    return JsonResponse({'error': 'Invalid request'})



def employee_dashboard(request):
    try:
        employee_id = request.session['employee_id']
    except:
        return redirect('employee_login')

    admin_id = request.session.get('admin_id')
    current_date = date.today()
    employee_id = request.session.get('employee_id')

    # Retrieve assigned tasks from Firebase for the current employee
    leave_request_status_ref = db.reference(f'leave_requests/{employee_id}/status')
    leave_request_status = leave_request_status_ref.get()

    # Assigned tasks
    assigned_tasks_ref = db.reference(f'tasks/{employee_id}')
    assigned_tasks_data = assigned_tasks_ref.get()

    # Convert the tasks data to a list with task ID included
    assigned_tasks = []
    if assigned_tasks_data is not None:
        for task_id, task_data in assigned_tasks_data.items():
            task_data['task_id'] = task_id
            assigned_tasks.append(task_data)
    # End assigned tasks

    # Initialize other variables with default values
    punch_in_count = 0
    punch_out_count = 0
    employee_name = ""

    leave_requests_ref = db.reference(f'leave_requests/{employee_id}')
    leave_requests = leave_requests_ref.get()

    with connection.cursor() as cursor:
        # Check if the employee has punched in on the current date
        cursor.execute("SELECT COUNT(*) FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s AND DATE(Start_Time) = %s", (employee_id, current_date))
        result = cursor.fetchone()
        if result is not None:  # Check for None
            punch_in_count = result[0]

        # Check if the employee has punched out on the current date
        cursor.execute("SELECT COUNT(*) FROM EMPLOYEE_ATTENDANCE WHERE EmployeeID = %s AND DATE(End_Time) = %s", (employee_id, current_date))
        result = cursor.fetchone()
        if result is not None:  # Check for None
            punch_out_count = result[0]

        cursor.execute("SELECT Name FROM Employee WHERE EmployeeID = %s", (employee_id,))
        result = cursor.fetchone()
        if result is not None:  # Check for None
            employee_name = result[0]

    return render(request, 'user_panel_template/employee_dashboard.html', {
        'punch_in_count': punch_in_count,
        'punch_out_count': punch_out_count,
        'assigned_tasks': assigned_tasks,
        'employee_name': employee_name,
        'leave_request_status': leave_request_status,
        'leave_requests': leave_requests,
        'admin_id': admin_id,
        'current_date': date.today(),
    })

# Existing code


def mark_task_completed(request, employee_id, task_id):

    try:
        employee_id = request.session['employee_id']
    except:
        return redirect('employee_login')
    print("Marking task as completed")  

    # Update the status of the task to 'completed' in Firebase
    task_ref = db.reference(f'tasks/{employee_id}/{task_id}')
    task_ref.update({
        'status': 'completed',
    })

    return JsonResponse({'status': 'success'})



def edit_employee_data(request):
    try:
        employee_id = request.session['employee_id']
    except:
        return redirect('employee_login')
    if request.method == 'POST':
        try:
            # Get the data from the form
            name = request.POST['name']
            mobile = request.POST['mobile_number']
            email = request.POST['email']
            education = request.POST['education']
            new_password = request.POST['new_password']  # New password field
            employee_id = request.session.get('employee_id')

            with conn.cursor() as cursor:
                # Define the SQL UPDATE statement
                update_query = "UPDATE Employee SET Name = %s, MobileNumber = %s, EmailID = %s, education = %s, password = %s WHERE EmployeeID = %s"
                values = (name, mobile, email, education, new_password, employee_id)  # Include new password

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
        cursor = conn.cursor()
        # Retrieve the existing employee data based on the employee ID
        query = "SELECT Name, MobileNumber, EmailID, education, position, salary, password FROM Employee WHERE EmployeeID = %s"
        cursor.execute(query, (employee_id,))
        existing_employee = cursor.fetchone()
        return existing_employee

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None


@csrf_exempt
def leave_request(request):
    try:
        employee_id = request.session['employee_id']
    except:
        return redirect('employee_login')

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
        cursor = conn.cursor()
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
    try:
        employee_id = request.session['employee_id']
    except:
        return redirect('employee_login')

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

def show_details(request):
    try:
        employee_id = request.session['employee_id']
    except:
        return redirect('employee_login')
    
    employee_id = request.session.get('employee_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Employee WHERE EmployeeID = %s", (employee_id,))
        employee = cursor.fetchone()

    penualty = employee[-1] 

    # Convert the faceImage blob to base64 encoding for displaying in HTML
    if employee and employee[8]:
        employee_image_base64 = base64.b64encode(employee[8]).decode('utf-8')
        employee = employee[:8] + (employee_image_base64,)
    else:
        employee = employee[:8] + (None,)

    return render(request, 'user_panel_template/show_details.html', {'employee': employee, 'penualty': penualty})