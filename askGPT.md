i am developing an employee management system, in that it has feature like punch in punch out, i integrated new features and punch in punch out not working properly, i have backup for old code

working punch code
def employee_dashboard(request):
    current_date = date.today()
    employee_id = request.session.get('employee_id')

    leave_request_status_ref = db.reference(f'leave_requests/{employee_id}/status')
    leave_request_status = leave_request_status_ref.get()

    assigned_tasks_ref = db.reference(f'tasks/{employee_id}')
    assigned_tasks = assigned_tasks_ref.get()
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
        task_id = date.today().strftime('%Y%m%d%H%M%S')
    return render(request, 'user_panel_template/employee_dashboard.html', {
        'punch_in_count': punch_in_count,
        'punch_out_count': punch_out_count,
        'assigned_tasks': assigned_tasks,
        'employee_name': employee_name,
        'leave_request_status': leave_request_status,
        'leave_requests': leave_requests,
        'admin_id': admin_id,
        'current_date': date.today(),  # Include current_date in the context
        'task_id': task_id,  # Include the generated task_id in the context
    })



after updated and its not working.

def employee_dashboard(request):
    admin_id = request.session.get('admin_id')
    current_date = date.today()
    employee_id = request.session.get('employee_id')

    # Retrieve assigned tasks from Firebase for the current employee
    leave_request_status_ref = db.reference(f'leave_requests/{employee_id}/status')
    leave_request_status = leave_request_status_ref.get()

    # assigned task
    assigned_tasks_ref = db.reference(f'tasks/{employee_id}')
    assigned_tasks_data = assigned_tasks_ref.get()

    # Convert the tasks data to a list with task ID included
    assigned_tasks = []
    if assigned_tasks_data is not None:
        for task_id, task_data in assigned_tasks_data.items():
            task_data['task_id'] = task_id
            assigned_tasks.append(task_data)
    # end assigned task

    # Initialize other variables with default values
    punch_in_count = 0
    punch_out_count = 0
    employee_name = ""

    leave_requests_ref = db.reference(f'leave_requests/{employee_id}')
    leave_requests = leave_requests_ref.get()

    # Your existing code for getting punch counts, employee name, etc.

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


brainstorm and merge this