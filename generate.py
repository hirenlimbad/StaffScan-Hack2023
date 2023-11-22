import datetime
import random

# Function to generate SQL insert query for a given employee ID and date
def generate_insert_query(employee_id, date):
    start_time = date.replace(hour=9, minute=0, second=0)
    end_time = date.replace(hour=18, minute=0, second=0)

    # Simulate a 80% chance of attendance for a given day
    is_present = 1 if random.random() < 0.8 else 0

    return f"({employee_id}, '{start_time}', '{end_time}', NULL, NULL, {is_present})"

# Function to generate SQL insert queries for a range of employee IDs and the past 1 week
def generate_insert_queries(start_employee_id, end_employee_id):
    current_date = datetime.datetime.now()

    # Generate queries for the past 1 week
    insert_queries = []
    for employee_id in range(start_employee_id, end_employee_id + 1):
        for day in range(7):
            date = current_date - datetime.timedelta(days=day)
            insert_queries.append(generate_insert_query(employee_id, date))

    return "INSERT INTO `EMPLOYEE_ATTENDANCE` (`EmployeeID`, `Start_Time`, `End_Time`, `leave_start`, `leave_end`, `islate`) VALUES\n" + ",\n".join(insert_queries) + ";"

# Example: Generate insert queries for employee IDs 533 to 541
insert_queries = generate_insert_queries(533, 535)
print(insert_queries)
