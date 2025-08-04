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
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `ticket_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `email` varchar(150) NOT NULL,
  `department` enum('IT','HR','Manager') NOT NULL,
  `gender` enum('Male','Female','Other') NOT NULL,
  `women_safety` tinyint(1) DEFAULT '0',
  `description` text NOT NULL,
  `severity_level` enum('1','2','3') NOT NULL,
  `status` enum('Open','In Progress','Resolved','Closed') DEFAULT 'Open',
  `submitted_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ticket_id`),
  KEY `employee_id` (`employee_id`),
  CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tickets`
--

LOCK TABLES `tickets` WRITE;
/*!40000 ALTER TABLE `tickets` DISABLE KEYS */;
INSERT INTO `tickets` VALUES (1,24,'avi@example.com','IT','Male',0,'Network connectivity issues in the office.','2','Open','2025-07-22 00:58:52'),(2,25,'meena@example.com','HR','Female',0,'Request for leave approval delayed.','1','In Progress','2025-07-24 00:58:52'),(3,26,'raj@example.com','Manager','Male',0,'Need assistance with project deadlines.','3','Resolved','2025-07-27 00:58:52'),(4,27,'sara@example.com','IT','Female',1,'Concern about office safety after hours.','2','Open','2025-07-28 00:58:52'),(5,28,'tom@example.com','Manager','Male',0,'Equipment malfunction in the lab.','3','Closed','2025-07-17 00:58:52'),(6,29,'nina@example.com','HR','Female',0,'Issue with payroll processing.','1','Open','2025-07-29 00:58:52'),(7,30,'john@example.com','IT','Male',0,'Software installation request pending.','2','In Progress','2025-07-25 00:58:52'),(8,31,'lisa@example.com','Manager','Female',0,'Project budget approval needed.','3','Resolved','2025-07-26 00:58:52'),(9,32,'mike@example.com','HR','Male',0,'Training session scheduling conflict.','1','Closed','2025-07-12 00:58:52'),(10,33,'olga@example.com','IT','Female',1,'Security concern regarding data access.','3','Open','2025-07-30 00:58:52');
/*!40000 ALTER TABLE `tickets` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:37
