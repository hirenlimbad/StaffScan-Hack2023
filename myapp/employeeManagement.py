from PIL import Image
import os
import mysql.connector
from django.shortcuts import render,HttpResponse
import mysql.connector
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render
import csv
from io import TextIOWrapper
from django.db import connection as conn


class employeeManagement:
    """
    A class for managing employee data in a MySQL database.
    """

    def __init__(self):
        self.conn = conn

    def checkCredentials(self, username, password):
        """
        Checks if the given username and password match an admin login in the database.

        Args:
            username (str): The username to check.
            password (str): The password to check.

        Returns:
            bool: True if the credentials match an admin login, False otherwise.
        """
        query = "SELECT * FROM admin_login WHERE username = %s AND password = %s"
        cursor = self.conn.cursor()
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        return user[0] if user else None

    def saveEmployeeForm(self, form, admin_id):
        """
        Saves employee data from a Django form to the database.

        Args:
            form (EmployeeForm): The form containing the employee data.
        """
        print("Going to save Employee data.")

        name = form.cleaned_data.get('name')
        mobile = form.cleaned_data.get('mobile_number')
        email = form.cleaned_data.get('email')
        password = email
        education = form.cleaned_data.get('education')
        position = form.cleaned_data.get('position')
        salary = form.cleaned_data.get('salary')
        photo1 = form.cleaned_data.get('faceImage').read()  # Read the binary data from the image file

        try:
            # Create a cursor
            cursor = self.conn.cursor()

            # Define the SQL INSERT statement
            insert_query = "INSERT INTO Employee (Name, MobileNumber, EmailID, password, education, position, salary, faceImage, admin_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # Execute the INSERT statement with the values
            cursor.execute(insert_query, (name, mobile, email, password, education, position, salary, photo1, admin_id))

            # Commit the transaction
            self.conn.commit()

            # Close the cursor and connection
            # cursor.close()
            # self.conn.close()

            print("Employee data saved successfully.")

        except mysql.connector.Error as e:
            print(f"Error: {e}")

    def showAllEmployees(self, admin_id=3):
        """
        Retrieves all employee data from the database.

        Returns:
            list: A list of dictionaries containing employee data.
        """
        cursor = self.conn.cursor()  # Use dictionary cursor to fetch data as dictionaries
        print(admin_id)
        # Define your SQL query to fetch employee data
        sql_query = "SELECT EmployeeID, Name, MobileNumber, EmailID FROM Employee where admin_id = " + str(admin_id)

        cursor.execute(sql_query)
        employees = cursor.fetchall()
        print(employees)

        # cursor.close()
        return employees

    def isPresent(self):
        """
        Retrieves the IDs of all employees who are currently present at work.

        Returns:
            list: A list of integers representing the IDs of present employees.
        """
        cursor = self.conn.cursor()
        sql_query = "SELECT EmployeeID FROM EMPLOYEE_ATTENDANCE WHERE DATE(Start_Time) = CURDATE() AND End_Time IS NULL"
        cursor.execute(sql_query)
        present_employees = cursor.fetchall()
        present_id = []
        for i in present_employees:
            present_id.append(i[0])
        return present_id

    def updateEmployeeForm(self, request):
        """
        Updates employee data in the database based on a Django form.

        Args:
            request (django.http.request.HttpRequest): The HTTP request containing the form data.

        Returns:
            django.shortcuts.render: A rendered HTML template showing all employees in the database.
        """
        if request.method == 'POST':
            try:
                # Get the data from the form
                name = request.POST['name']
                mobile = request.POST['mobile_number']
                email = request.POST['email']
                photo = request.FILES.get('photo')
                id = request.POST['id']

                # Create a cursor
                cursor = self.conn.cursor()

                # Define the SQL UPDATE statement
                update_query = "UPDATE Employee SET name = %s, MobileNumber = %s, EmailID = %s"
                values = (name, mobile, email)

                if photo:
                    update_query += ", faceImage = %s"
                    values = (name, mobile, email, photo.read())

                update_query += " WHERE EmployeeID = " +id

                # Execute the UPDATE statement with the values
                cursor.execute(update_query, values)

                # Commit the changes to the database
                self.conn.commit()

                cursor.close()
                print("done")
                return render(request, 'showEmployee.html', {'employees': employeeManagement().showAllEmployees()})
            except mysql.connector.Error as e:
                return HttpResponse(f"Error: {e}")

        return render(request, 'update_employee_form.html')

    def upload_csv(self,request):
        if request.method == 'POST' and request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):
                return HttpResponse('Not a CSV file')

            # Assuming you have a MySQL connection (self.conn) established

            try:
                with TextIOWrapper(csv_file.file, encoding='utf-8') as file:
                    csv_data = csv.reader(file)
                    next(csv_data)  # Skip the header row


                    for row in csv_data:
                        try:
                            name, mobile, email, education, position, salary = row
                            password = email  # Using email as password

                            cursor = self.conn.cursor()
                            insert_query = "INSERT INTO Employee (Name, MobileNumber, EmailID, password, education, position, salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                            cursor.execute(insert_query, (name, mobile, email, password, education, position, salary))
                            self.conn.commit()
                            cursor.close()
                        except Exception:
                            pass

            except Exception as e:
                return HttpResponse(f'Error: {e}')

            return HttpResponseRedirect('../showEmployee.html')



        return render(request, 'upload_csv.html')


    def __del__(self):
        pass
        """
        Closes the database connection when the employeeManagement instance is destroyed.
        """
        # self.conn.close()


if __name__ == "__main__":
    employeeManagement().isPresent()