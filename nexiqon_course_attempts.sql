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
-- Table structure for table `course_attempts`
--

DROP TABLE IF EXISTS `course_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_attempts` (
  `attempt_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int DEFAULT NULL,
  `course_id` int DEFAULT NULL,
  `score` int DEFAULT NULL,
  `total_questions` int DEFAULT '20',
  `passed` tinyint(1) DEFAULT '0',
  `answers_json` text,
  `attempt_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`attempt_id`),
  KEY `employee_id` (`employee_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `course_attempts_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`),
  CONSTRAINT `course_attempts_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course_catalog` (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_attempts`
--

LOCK TABLES `course_attempts` WRITE;
/*!40000 ALTER TABLE `course_attempts` DISABLE KEYS */;
INSERT INTO `course_attempts` VALUES (16,24,4,18,20,1,'{\"Q1\":\"A\",\"Q2\":\"B\",\"Q3\":\"C\"}','2025-08-01 00:36:52'),(17,25,5,14,20,0,'{\"Q1\":\"B\",\"Q2\":\"D\",\"Q3\":\"A\"}','2025-07-31 00:36:52'),(18,26,6,20,20,1,'{\"Q1\":\"C\",\"Q2\":\"C\",\"Q3\":\"D\"}','2025-07-30 00:36:52'),(19,27,4,12,20,0,'{\"Q1\":\"A\",\"Q2\":\"A\",\"Q3\":\"B\"}','2025-07-29 00:36:52'),(20,28,5,19,20,1,'{\"Q1\":\"D\",\"Q2\":\"C\",\"Q3\":\"A\"}','2025-07-28 00:36:52'),(21,29,6,17,20,1,'{\"Q1\":\"C\",\"Q2\":\"D\",\"Q3\":\"B\"}','2025-07-27 00:36:52'),(22,30,4,13,20,0,'{\"Q1\":\"A\",\"Q2\":\"B\",\"Q3\":\"A\"}','2025-07-26 00:36:52'),(23,31,5,20,20,1,'{\"Q1\":\"B\",\"Q2\":\"B\",\"Q3\":\"B\"}','2025-07-25 00:36:52'),(24,32,6,15,20,0,'{\"Q1\":\"D\",\"Q2\":\"A\",\"Q3\":\"C\"}','2025-07-24 00:36:52'),(25,33,4,16,20,1,'{\"Q1\":\"C\",\"Q2\":\"C\",\"Q3\":\"D\"}','2025-07-23 00:36:52');
/*!40000 ALTER TABLE `course_attempts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:42
