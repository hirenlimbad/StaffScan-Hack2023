i need Attendance Reports, we will create an monthly report of employee attendance, 
here we have 2 models.

class Employee(models.Model):
    EmployeeID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255)
    MobileNumber = models.CharField(max_length=15, null=True, blank=True)
    EmailID = models.CharField(max_length=255, null=True, blank=True, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    education = models.CharField(max_length=25, null=True, blank=True)
    position = models.CharField(max_length=25, null=True, blank=True)
    salary = models.BigIntegerField(null=True, blank=True)
    faceImage = models.BinaryField(null=True, blank=True)
    remaining_leave = models.IntegerField(default=0)
    late_days = models.IntegerField(null=True, blank=True)
    admin_id = models.IntegerField(null=True, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.Name

class EmployeeAttendance(models.Model):
    AttendanceID = models.AutoField(primary_key=True)
    EmployeeID = models.ForeignKey(Employee, on_delete=models.CASCADE)
    Start_Time = models.DateTimeField(null=True, blank=True)
    End_Time = models.DateTimeField(null=True, blank=True)
    leave_start = models.DateTimeField(null=True, blank=True)
    leave_end = models.DateTimeField(null=True, blank=True)
    islate = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Attendance ID: {self.AttendanceID}, Employee: {self.EmployeeID}, Start Time: {self.Start_Time}, End Time: {self.End_Time}, Is Late: {self.islate}"


based on employee early arrival, late employee, overtime generate one report. based on it also show an employee currunt salary.
i am developing django application, i will create an new html page, where for perticular employee monthly report will be downloaded.