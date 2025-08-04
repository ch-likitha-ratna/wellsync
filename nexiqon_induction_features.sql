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
-- Table structure for table `induction_features`
--

DROP TABLE IF EXISTS `induction_features`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `induction_features` (
  `feature_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `description` text,
  `added_by` int DEFAULT NULL,
  `status` enum('Pending','Approved') DEFAULT 'Pending',
  PRIMARY KEY (`feature_id`),
  KEY `added_by` (`added_by`),
  CONSTRAINT `induction_features_ibfk_1` FOREIGN KEY (`added_by`) REFERENCES `employee` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `induction_features`
--

LOCK TABLES `induction_features` WRITE;
/*!40000 ALTER TABLE `induction_features` DISABLE KEYS */;
INSERT INTO `induction_features` VALUES (1,'Welcome Tour Video','A short video that gives new hires a quick overview of the office.',24,'Approved'),(2,'Interactive Handbook','Digital version of employee handbook with navigation and search.',25,'Pending'),(3,'Gamified Orientation','Game-based orientation process to make learning engaging.',26,'Approved'),(4,'Mentor Matching Tool','Automatically assigns mentors to new employees.',27,'Pending'),(5,'Buddy Checklist','Checklist for employee buddies to support onboarding.',28,'Approved'),(6,'Feedback Form','Allows new hires to submit feedback post-induction.',29,'Pending'),(7,'Onboarding Quiz','Verifies understanding of key company policies.',30,'Approved'),(8,'Live Q&A Session','Weekly Q&A with HR and IT teams during onboarding.',31,'Pending'),(9,'Department Directory','Clickable org chart of all departments and leads.',32,'Approved'),(10,'Progress Tracker','Monitors each induction module completion status.',33,'Pending');
/*!40000 ALTER TABLE `induction_features` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:29
