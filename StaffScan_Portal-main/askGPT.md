<!DOCTYPE html>
<html>
<head>
    <title>Employee Late Days</title>
    <!-- Include Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container">
        <h1 class="mt-3">Late Employee</h1>
        <table class="table table-striped table-bordered mt-3">
            <thead class="thead-dark">
                <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Position</th>
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
                        <td>{{ employee.late_days }}</td>
                        <td>{{ employee.consecutive_late }}</td>
                        <td><button class="btn btn-primary">Penalty</button></td> <!-- Button in the new column -->
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Include Bootstrap JS and Popper.js for Bootstrap features (optional) -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
