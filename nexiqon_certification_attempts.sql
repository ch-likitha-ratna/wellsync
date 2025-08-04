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
-- Table structure for table `certification_attempts`
--

DROP TABLE IF EXISTS `certification_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certification_attempts` (
  `attempt_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int DEFAULT NULL,
  `badge_id` int DEFAULT NULL,
  `attempt_date` date DEFAULT NULL,
  `result` enum('Pass','Fail') DEFAULT NULL,
  PRIMARY KEY (`attempt_id`),
  KEY `employee_id` (`employee_id`),
  KEY `badge_id` (`badge_id`),
  CONSTRAINT `certification_attempts_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`),
  CONSTRAINT `certification_attempts_ibfk_2` FOREIGN KEY (`badge_id`) REFERENCES `badge_catalog` (`badge_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certification_attempts`
--

LOCK TABLES `certification_attempts` WRITE;
/*!40000 ALTER TABLE `certification_attempts` DISABLE KEYS */;
INSERT INTO `certification_attempts` VALUES (1,24,1,'2023-01-15','Pass'),(2,25,2,'2023-02-20','Fail'),(3,26,3,'2023-03-10','Pass'),(4,27,1,'2023-04-05','Pass'),(5,28,2,'2023-05-12','Fail'),(6,29,3,'2023-06-18','Pass'),(7,30,1,'2023-07-22','Pass'),(8,31,2,'2023-08-30','Fail'),(9,32,3,'2023-09-15','Pass'),(10,33,1,'2023-10-10','Pass');
/*!40000 ALTER TABLE `certification_attempts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:40
