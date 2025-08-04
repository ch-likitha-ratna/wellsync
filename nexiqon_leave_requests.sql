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
-- Table structure for table `leave_requests`
--

DROP TABLE IF EXISTS `leave_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leave_requests` (
  `leave_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `leave_type` enum('Paid','Unpaid') NOT NULL,
  `sub_type` enum('Sick','Personal') DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `total_days` int GENERATED ALWAYS AS (((to_days(`end_date`) - to_days(`start_date`)) + 1)) STORED,
  `reason` text,
  `status` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `rejection_reason` text,
  `approved_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`leave_id`),
  KEY `employee_id` (`employee_id`),
  KEY `approved_by` (`approved_by`),
  CONSTRAINT `leave_requests_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`),
  CONSTRAINT `leave_requests_ibfk_2` FOREIGN KEY (`approved_by`) REFERENCES `employee` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_requests`
--

LOCK TABLES `leave_requests` WRITE;
/*!40000 ALTER TABLE `leave_requests` DISABLE KEYS */;
INSERT INTO `leave_requests` (`leave_id`, `employee_id`, `leave_type`, `sub_type`, `start_date`, `end_date`, `reason`, `status`, `rejection_reason`, `approved_by`, `created_at`) VALUES (1,24,'Paid','Sick','2025-07-01','2025-07-03','Flu and fever','Approved',NULL,30,'2025-07-17 00:51:49'),(2,25,'Unpaid','Personal','2025-08-10','2025-08-12','Family emergency','Pending',NULL,NULL,'2025-07-25 00:51:49'),(3,26,'Paid','Personal','2025-09-05','2025-09-06','Personal matters','Rejected','Insufficient leave balance',31,'2025-07-12 00:51:49'),(4,27,'Paid','Sick','2025-06-15','2025-06-16','Minor surgery recovery','Approved',NULL,32,'2025-07-02 00:51:49'),(5,28,'Unpaid','Personal','2025-07-20','2025-07-22','Vacation extended','Pending',NULL,NULL,'2025-07-27 00:51:49'),(6,29,'Paid','Sick','2025-07-25','2025-07-25','Doctor appointment','Approved',NULL,33,'2025-07-29 00:51:49'),(7,30,'Paid','Personal','2025-08-01','2025-08-02','Moving house','Rejected','Project deadline conflict',34,'2025-07-20 00:51:49'),(8,31,'Unpaid','Sick','2025-07-28','2025-07-29','Recovering from cold','Pending',NULL,NULL,'2025-07-24 00:51:49'),(9,32,'Paid','Personal','2025-06-10','2025-06-12','Family function','Approved',NULL,35,'2025-07-07 00:51:49'),(10,33,'Unpaid','Sick','2025-09-01','2025-09-02','Medical tests','Rejected','Late application',36,'2025-07-14 00:51:49');
/*!40000 ALTER TABLE `leave_requests` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:32
