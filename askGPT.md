in employee attendance system i have one table structure where it has penulty to employee for who employees are late. see i have UI for that give me an sql query for that if penulty applies than islate == 0 in the employee attendance table for respective employee.





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
    cursor.execute("SELECT penalty FROM Employee WHERE EmployeeID = %s", (employee_id,))
    penalty = cursor.fetchone()[0]

    # Calculate the new salary after reducing by 1000
    new_salary = penalty + 1000

    # Update the salary in the database
    update_query = "UPDATE Employee SET penalty = %s WHERE EmployeeID = %s"
    cursor.execute(update_query, (penalty, employee_id))
    conn.commit()
    return redirect('late_employee')

CREATE TABLE `EMPLOYEE_ATTENDANCE` (
  `AttendanceID` int NOT NULL AUTO_INCREMENT,
  `EmployeeID` int DEFAULT NULL,
  `Start_Time` datetime DEFAULT NULL,
  `End_Time` datetime DEFAULT NULL,
  `leave_start` datetime DEFAULT NULL,
  `leave_end` datetime DEFAULT NULL,
  `islate` tinyint DEFAULT NULL,
  PRIMARY KEY (`AttendanceID`),
  KEY `EmployeeID` (`EmployeeID`),
  CONSTRAINT `fk_employee_attendance` FOREIGN KEY (`EmployeeID`) REFERENCES `Employee` (`EmployeeID`),
  CONSTRAINT `fk_employee_attendance_employee` FOREIGN KEY (`EmployeeID`) REFERENCES `Employee` (`EmployeeID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


template code,
{% extends "navbar.html" %}
{% block title %}Home{% endblock title %}
{% block body %}


<!DOCTYPE html>
<html>
<head>
    <title>Employee Late Days</title>
    <!-- Include Bootstrap CSS -->
    <!-- <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"> -->
    <!-- Include CSRF Token -->

    <style>

        body {
            color: white;
            font-family: Arial, sans-serif;
        }
    </style>
    {% csrf_token %}
</head>
<body>
    <div class="container">
        <h1 class="mt-3">Late Employee</h1>
        <table class="table">
            <thead class="thead-dark">
                <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Position</th>
                    <th>Last Punch In Time</th>
                    <th>Late Days</th>
                    <th>Consecutive Late</th>
                    <th>Penalty</th> <!-- New column for the "Penalty" button -->
                </tr>
            </thead>
            <tbody>
                {% for employee in employees %}
                    <tr>
                        <td>{{ employee.EmployeeID }}</td>
                        <td>{{ employee.Name }}</td>
                        <td>{{ employee.Position }}</td>
                        <td>{{ employee.last_punch_in_time }}</td>
                        <td>{{ employee.late_days }}</td>
                        <td>{{ employee.consecutive_late }}</td>
                        <td><button class="btn btn-primary penalty-button" data-employeeid="{{ employee.EmployeeID }}">Penalty</button></td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Include Bootstrap JS and Popper.js for Bootstrap features (optional) -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            $('.penalty-button').click(function() {
                var employeeID = $(this).data('employeeid');

                $.ajax({
                    type: 'POST',
                    url: '/apply_penalty/' + employeeID + '/', // Define the correct URL based on your project structure
                    data: { csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val() },
                    success: function(response) {
                        // Handle the response from the server, e.g., show a success message
                        console.log(response);
                    }
                });
            });
        });
    </script>
</body>
</html>
{% endblock body %}
