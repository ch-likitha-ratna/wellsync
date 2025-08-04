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
-- Table structure for table `induction_content`
--

DROP TABLE IF EXISTS `induction_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `induction_content` (
  `induction_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `description` text,
  `added_by` int DEFAULT NULL,
  `added_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`induction_id`),
  KEY `added_by` (`added_by`),
  CONSTRAINT `induction_content_ibfk_1` FOREIGN KEY (`added_by`) REFERENCES `employee` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `induction_content`
--

LOCK TABLES `induction_content` WRITE;
/*!40000 ALTER TABLE `induction_content` DISABLE KEYS */;
INSERT INTO `induction_content` VALUES (1,'Company Overview','An introduction to the company’s mission, vision, and history.',24,'2025-08-01 00:44:26'),(2,'Code of Conduct','Detailed overview of behavioral expectations and ethics policies.',25,'2025-07-31 00:44:26'),(3,'IT Policies','Guidelines for secure and responsible use of IT resources.',26,'2025-07-30 00:44:26'),(4,'HR Policies & Benefits','Explains leave policies, insurance, reimbursements, etc.',27,'2025-07-29 00:44:26'),(5,'Security Protocols','Covers access control, data privacy, and emergency procedures.',28,'2025-07-28 00:44:26'),(6,'Performance Expectations','Outlines how employee performance is measured and reviewed.',29,'2025-07-27 00:44:26'),(7,'Team Structure','Breakdown of departments, key contacts, and reporting hierarchy.',30,'2025-07-26 00:44:26'),(8,'Tools & Platforms','Introduction to internal tools and software used across teams.',31,'2025-07-25 00:44:26'),(9,'First Week Plan','Checklist and expectations for the first 5 working days.',32,'2025-07-24 00:44:26'),(10,'Support Contacts','List of go-to people for IT, HR, Admin, and more.',33,'2025-07-23 00:44:26');
/*!40000 ALTER TABLE `induction_content` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:41
