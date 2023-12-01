create database hackathon;

CREATE TABLE `admin_login` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `Employee` (
  `EmployeeID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `MobileNumber` varchar(15) DEFAULT NULL,
  `EmailID` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `education` varchar(25) DEFAULT NULL,
  `position` varchar(25) DEFAULT NULL,
  `salary` bigint DEFAULT NULL,
  `faceImage` mediumblob,
  `remaining_leave` int DEFAULT '0',
  `late_days` int DEFAULT NULL,
  `admin_id` int DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `penalty` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`EmployeeID`),
  UNIQUE KEY `EmailID` (`EmailID`),
  KEY `fk_admin` (`admin_id`),
  CONSTRAINT `fk_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin_login` (`admin_id`),
  CONSTRAINT `fk_admin_employee` FOREIGN KEY (`admin_id`) REFERENCES `admin_login` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;