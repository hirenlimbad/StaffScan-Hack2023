brainstorm
in employee attendance system i have one table structure where it shows employee start time and end time.instead i want a calendar with all days. if employee present than it calendar will show different color for that day.

here is my relavent code
def view_employee(request, employee_id):
    try:
        admin_id = request.session['admin_id']
    except KeyError:
        return redirect('login-page')

    # Fetch employee details
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EmployeeID, Name, MobileNumber, EmailID, password, education, position, salary, faceImage FROM Employee WHERE EmployeeID = %s",
            (employee_id,))
        employee = cursor.fetchone()

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
                'Start_Time': datetime.strftime(row[1], '%Y-%m-%d %H:%M:%S') if row[1] else None,
                'End_Time': datetime.strftime(row[2], '%Y-%m-%d %H:%M:%S') if row[2] else None,
                'leave_start': row[3],
                'leave_end': row[4],
                'islate': row[5]
            }
            attendance_data.append(entry)
        print(attendance_data)
    # Pass the data to the template for rendering
    return render(request, 'view_employee.html', {'employee': employee, 'attendance_data': attendance_data})


template code
 <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Punch-In Time</th>
                        <th>Punch-Out Time</th>
                        <th>Is Late</th>
                    </tr>
                </thead>
                <tbody>
                    {% for entry in attendance_data %}
                        <tr>
                            <td>{{ entry.Start_Time }}</td>
                            <td>{{ entry.Start_Time }}</td>
                            <td>{% if entry.End_Time %}{{ entry.End_Time }}{% else %}Missed{% endif %}</td>
                            <td>{{ entry.islate }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
