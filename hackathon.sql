
-- username : unknown
-- password : password
-- database : hackathon
-- port : 3306


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
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE DATABASE `hackathon` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

use hackathon;

INSERT INTO `Employee` (`EmployeeID`,`Name`, `MobileNumber`, `EmailID`, `password`, `education`, `position`, `salary`, `faceImage`, `remaining_leave`, `late_days`, `admin_id`, `arrival_time`, `penalty`)
VALUES (1,'Ishan Purohit', '9998084322', 'ipurohit7654@gmail.com', 'ipurohit7654@gmail.com', 'Diploma in IT.', 'senior_developer', 51001, NULL, 20, 2, 3, '08:00:00', 1000.00);

INSERT INTO `Employee` (`EmployeeID`,`Name`, `MobileNumber`, `EmailID`, `password`, `education`, `position`, `salary`, `faceImage`, `remaining_leave`, `late_days`, `admin_id`, `arrival_time`, `penalty`)
VALUES (2,'Hiren Limbad', '7698265327', 'limbadhiren00@gmail.com', 'limbadhiren00@gmail.com', 'Diploma in IT.', 'junior_developer', 51101, NULL, 18, 1, 3, '08:00:00', 800.00);

INSERT INTO `Employee` (`EmployeeID`,`Name`, `MobileNumber`, `EmailID`, `password`, `education`, `position`, `salary`, `faceImage`, `remaining_leave`, `late_days`, `admin_id`, `arrival_time`, `penalty`)
VALUES (3,'Jay Changani', '9408842056', 'jaychangani2005@gmail.com', 'jaychangani2005@email.com', 'Diploma in IT.', 'manager', 51501, NULL, 15, 3, 3, '08:00:00', 1200.00);

INSERT INTO `Employee` (`EmployeeID`,`Name`, `MobileNumber`, `EmailID`, `password`, `education`, `position`, `salary`, `faceImage`, `remaining_leave`, `late_days`, `admin_id`, `arrival_time`, `penalty`)
VALUES (4,'Vivek Kantariya', '9104053837', 'vivekkantariya@gmail.com', 'vivekkantariya@email.com', 'Diploma in IT.', 'senior_developer', 51001, NULL, 12, 0, 3, '08:00:00', 1500.00);

INSERT INTO `Employee` (`EmployeeID`,`Name`, `MobileNumber`, `EmailID`, `password`, `education`, `position`, `salary`, `faceImage`, `remaining_leave`, `late_days`, `admin_id`, `arrival_time`, `penalty`)
VALUES (5,'Radhika Mer', '7435807633', 'radhikajmer@gmail.com', 'radhikajmer@gmail.com', 'Diploma in IT', 'manager', 51001, NULL, 10, 2, 3, '08:00:00', 1000.00);

INSERT INTO `Employee` (`EmployeeID`,`Name`, `MobileNumber`, `EmailID`, `password`, `education`, `position`, `salary`, `faceImage`, `remaining_leave`, `late_days`, `admin_id`, `arrival_time`, `penalty`)
VALUES (6,'Rajesh Patel', '9998084322', 'rajeshpatel@gmail.com', 'rajeshpatel@gmail.com', 'B. Tech.', 'senior_developer', 51001, NULL, 20, 2, 3, '08:00:00', 1000.00);