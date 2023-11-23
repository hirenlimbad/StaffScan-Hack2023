import datetime
import random


# function to get random minute
def getRandMinute():
    return random.randint(0, 59)

# Function to generate SQL insert query for a given employee ID and date
def generate_insert_query(employee_id, date):

    # start time will randomly be between 9:00 AM and 10:00 AM at any minute
    start_time = date.replace(hour=9 , minute = getRandMinute(), second=0)
    end_time =  date.replace(hour=18 , minute = getRandMinute(), second=0)

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
insert_queries = generate_insert_queries(1,6)
print(insert_queries)
