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
-- Table structure for table `employee_badges`
--

DROP TABLE IF EXISTS `employee_badges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_badges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `badge_id` int NOT NULL,
  `awarded_on` date DEFAULT (curdate()),
  PRIMARY KEY (`id`),
  KEY `employee_id` (`employee_id`),
  KEY `badge_id` (`badge_id`),
  CONSTRAINT `employee_badges_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`) ON DELETE CASCADE,
  CONSTRAINT `employee_badges_ibfk_2` FOREIGN KEY (`badge_id`) REFERENCES `badge_catalog` (`badge_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee_badges`
--

LOCK TABLES `employee_badges` WRITE;
/*!40000 ALTER TABLE `employee_badges` DISABLE KEYS */;
INSERT INTO `employee_badges` VALUES (1,24,1,'2025-07-22'),(2,25,2,'2025-07-23'),(3,26,3,'2025-07-24'),(4,27,1,'2025-07-25'),(5,28,2,'2025-07-26'),(6,29,3,'2025-07-27'),(7,30,1,'2025-07-28'),(8,31,2,'2025-07-29'),(9,32,3,'2025-07-30'),(10,33,1,'2025-07-31');
/*!40000 ALTER TABLE `employee_badges` ENABLE KEYS */;
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
