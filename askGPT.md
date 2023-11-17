
CREATE TABLE `EMPLOYEE_ATTENDANCE` (
  `AttendanceID` int NOT NULL AUTO_INCREMENT,
  `EmployeeID` int DEFAULT NULL,
  `Start_Time` datetime DEFAULT NULL,
  `End_Time` datetime DEFAULT NULL,
  `leave_start` datetime DEFAULT NULL,
  `leave_end` datetime DEFAULT NULL,
  `islate` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`AttendanceID`),
  KEY `EmployeeID` (`EmployeeID`),
  CONSTRAINT `fk_employee_attendance` FOREIGN KEY (`EmployeeID`) REFERENCES `Employee` (`EmployeeID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



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
  PRIMARY KEY (`EmployeeID`),
  UNIQUE KEY `EmailID` (`EmailID`),
  KEY `fk_admin` (`admin_id`),
  CONSTRAINT `fk_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin_login` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `timings` (
  `admin_id` int DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `position` varchar(25) DEFAULT NULL,
  KEY `fk_admin` (`admin_id`),
  CONSTRAINT `fk_admin_newtable` FOREIGN KEY (`admin_id`) REFERENCES `admin_login` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
