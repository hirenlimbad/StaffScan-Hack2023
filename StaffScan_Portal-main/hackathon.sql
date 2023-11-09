
-- username : unknown
-- password : password
-- database : hackathon
-- port : 3306

CREATE DATABASE `hackathon` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

use hackathon;

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT, -- You may use your own ID system
    Name VARCHAR(255) NOT NULL,
    MobileNumber VARCHAR(15),
    EmailID VARCHAR(255),
    faceImage MEDIUMBLOB
);

CREATE TABLE admin_login (
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    MobileNumber VARCHAR(15),
    EmailID VARCHAR(255),
    faceImage MEDIUMBLOB
);

CREATE TABLE EMPLOYEE_ATTENDANCE (
    AttendanceID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT,
    Start_Time DATETIME NOT NULL,
    End_Time DATETIME,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID)
);

-- Inserting an attendance record with End_Time NULL for EmployeeID 1
INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, Start_Time, End_Time) 
VALUES (22, NOW(), NULL);

-- Inserting an attendance record with End_Time NULL for EmployeeID 2
INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, Start_Time, End_Time) 
VALUES (23, NOW(), NULL);

-- Inserting an attendance record with End_Time NULL for EmployeeID 3
INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, Start_Time, End_Time) 
VALUES (27, NOW(), NULL);

-- Inserting an attendance record with End_Time NULL for EmployeeID 4
INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, Start_Time, End_Time) 
VALUES (36, NOW(), NULL);

select * from admin_login;