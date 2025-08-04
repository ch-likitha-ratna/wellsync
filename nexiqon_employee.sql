-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: quadprserver.mysql.database.azure.com    Database: nexiqon
-- ------------------------------------------------------
-- Server version	8.0.41-azure

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee` (
  `employee_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `contact_number` varchar(15) NOT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `department` enum('CEO','CTO','Manager','HR','Employee','IT') NOT NULL,
  `role_title` varchar(100) DEFAULT NULL,
  `visa_type` varchar(50) DEFAULT NULL,
  `experience_years` decimal(4,1) DEFAULT NULL,
  `salary` decimal(12,2) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `leaves_sick` int DEFAULT '0',
  `leaves_personal` int DEFAULT '0',
  `comp_off` int DEFAULT '0',
  `project_id` int DEFAULT NULL,
  `manager_id` int DEFAULT NULL,
  `badges_earned` int DEFAULT NULL,
  `photo_blob` longblob,
  `status` enum('active','resigned','terminated') DEFAULT 'active',
  `joined_date` datetime DEFAULT NULL,
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `email` (`email`),
  KEY `fk_emp_manager` (`manager_id`),
  CONSTRAINT `fk_emp_manager` FOREIGN KEY (`manager_id`) REFERENCES `employee` (`employee_id`) ON DELETE SET NULL,
  CONSTRAINT `employee_chk_1` CHECK ((`salary` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee`
--

LOCK TABLES `employee` WRITE;
/*!40000 ALTER TABLE `employee` DISABLE KEYS */;
INSERT INTO `employee` VALUES (24,'John','Doe','john.doe@company.com','+1-1234567890','Male','CEO','CEO','H1B',15.0,120000.00,'New York',5,10,0,NULL,NULL,0,NULL,'active','2025-07-21 00:00:00'),(25,'Alice','Smith','alice.smith@company.com','+1-2345678901','Female','Employee','CTO','F1',12.0,110000.00,'Austin',5,10,0,NULL,NULL,0,NULL,'active','2025-07-21 00:00:00'),(26,'Michael','Brown','michael.brown@company.com','+1-3456789012','Male','Manager','HR Manager','H1B',10.0,100000.00,'San Francisco',5,10,0,NULL,NULL,0,NULL,'active','2025-07-21 00:00:00'),(27,'Liam','Martinez','liam.martinez@company.com','+1-8901234567','Male','Manager','Finance Manager','H1B',10.0,98000.00,'Los Angeles',5,10,0,NULL,NULL,0,NULL,'active','2025-07-21 00:00:00'),(28,'Nina','Wells','nina.wells@company.com','+1-1323456789','Female','Manager','Development Manager','H1B',11.0,102000.00,'San Jose',5,10,0,NULL,25,0,NULL,'active','2025-07-21 00:00:00'),(29,'Priya','Sharma','priya.sharma@company.com','+1-4567890123','Female','HR','HR Specialist','OPT',8.0,90000.00,'Chicago',5,10,0,NULL,26,0,NULL,'active','2025-07-21 00:00:00'),(30,'David','Lee','david.lee@company.com','+1-5678901234','Male','Employee','QA Engineer','H1B',6.0,85000.00,'Seattle',5,10,0,101,28,0,NULL,'active','2025-07-21 00:00:00'),(31,'Sahil','Kumar','sahil.kumar@company.com','+1-6789012345','Male','IT','System Administrator','OPT',9.0,95000.00,'New Jersey',5,10,0,102,25,0,NULL,'active','2025-07-21 00:00:00'),(32,'Ava','Nguyen','ava.nguyen@company.com','+1-7890123456','Female','Employee','Admin','F1',7.0,80000.00,'Dallas',5,10,0,103,25,0,NULL,'active','2025-07-21 00:00:00'),(33,'Olivia','Patel','olivia.patel@company.com','+1-9012345678','Female','Employee','Analyst','OPT',4.0,78000.00,'Atlanta',5,10,0,104,27,0,NULL,'active','2025-07-21 00:00:00'),(34,'Noah','Kim','noah.kim@company.com','+1-0123456789','Male','IT','Desktop Support','H1B',6.0,75000.00,'Houston',5,10,0,105,27,0,NULL,'active','2025-07-21 00:00:00'),(35,'Emma','Singh','emma.singh@company.com','+1-1023456789','Female','IT','Network Administrator','OPT',5.0,79000.00,'Boston',5,10,0,105,27,0,NULL,'active','2025-07-21 00:00:00'),(36,'Arjun','Verma','arjun.verma@company.com','+1-1123456789','Male','Employee','Azure Developer','OPT',3.0,82000.00,'Denver',5,10,0,106,28,0,NULL,'active','2025-07-21 00:00:00'),(37,'Sophia','Rao','sophia.rao@company.com','+1-1223456789','Female','Employee','Software Developer','OPT',2.0,81000.00,'Phoenix',5,10,0,106,28,0,NULL,'active','2025-07-21 00:00:00');
/*!40000 ALTER TABLE `employee` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:34
