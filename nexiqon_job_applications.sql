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
-- Table structure for table `job_applications`
--

DROP TABLE IF EXISTS `job_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `job_applications` (
  `application_id` int NOT NULL AUTO_INCREMENT,
  `job_id` int NOT NULL,
  `employee_id` int NOT NULL,
  `resume_path` varchar(255) DEFAULT NULL,
  `status` enum('Applied','Reviewed','Rejected','Shortlisted') DEFAULT 'Applied',
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`application_id`),
  KEY `job_id` (`job_id`),
  KEY `employee_id` (`employee_id`),
  KEY `reviewed_by` (`reviewed_by`),
  CONSTRAINT `job_applications_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `job_postings` (`job_id`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_3` FOREIGN KEY (`reviewed_by`) REFERENCES `employee` (`employee_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `job_applications`
--

LOCK TABLES `job_applications` WRITE;
/*!40000 ALTER TABLE `job_applications` DISABLE KEYS */;
INSERT INTO `job_applications` VALUES (1,1,24,'/resumes/avi_resume.pdf','Applied',NULL,NULL),(2,2,25,'/resumes/sarah_resume.pdf','Reviewed',30,'2025-07-30 00:51:00'),(3,3,26,'/resumes/john_resume.pdf','Rejected',31,'2025-07-31 00:51:00'),(4,4,27,'/resumes/emily_resume.pdf','Shortlisted',32,'2025-08-01 00:51:00'),(5,5,28,'/resumes/raj_resume.pdf','Applied',NULL,NULL),(6,1,29,'/resumes/lisa_resume.pdf','Reviewed',33,'2025-07-29 00:51:00'),(7,2,30,'/resumes/mike_resume.pdf','Applied',NULL,NULL),(8,3,31,'/resumes/nina_resume.pdf','Rejected',34,'2025-07-28 00:51:00'),(9,4,32,'/resumes/tom_resume.pdf','Shortlisted',35,'2025-07-31 00:51:00'),(10,5,33,'/resumes/olga_resume.pdf','Applied',NULL,NULL);
/*!40000 ALTER TABLE `job_applications` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:44
