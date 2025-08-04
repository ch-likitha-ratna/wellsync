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
-- Table structure for table `troubleshooting_docs`
--

DROP TABLE IF EXISTS `troubleshooting_docs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `troubleshooting_docs` (
  `doc_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `category` varchar(100) NOT NULL,
  `problem_description` text NOT NULL,
  `solution_steps` text NOT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`doc_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `troubleshooting_docs_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `employee` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `troubleshooting_docs`
--

LOCK TABLES `troubleshooting_docs` WRITE;
/*!40000 ALTER TABLE `troubleshooting_docs` DISABLE KEYS */;
INSERT INTO `troubleshooting_docs` VALUES (1,'WiFi Connectivity Issues','Network','Users are unable to connect to the WiFi network.','1. Restart the router\n2. Check SSID and password\n3. Verify DHCP settings\n4. Contact ISP if issue persists.',24,'2025-07-17 01:00:42'),(2,'Email Not Syncing','Email','Corporate email is not syncing on mobile devices.','1. Verify email account settings\n2. Remove and re-add the email account\n3. Check server status\n4. Reset device network settings.',25,'2025-07-20 01:00:42'),(3,'Software Installation Failure','Software','Installation of the new software fails with error code 123.','1. Check system requirements\n2. Disable antivirus temporarily\n3. Run installer as administrator\n4. Review logs for errors.',26,'2025-07-22 01:00:42'),(4,'Printer Offline','Hardware','Office printer shows offline status.','1. Check printer power and connection\n2. Restart printer and computer\n3. Reinstall printer drivers\n4. Check network printer settings.',27,'2025-07-24 01:00:42'),(5,'Slow Computer Performance','Hardware','User reports slow performance on their workstation.','1. Check running processes\n2. Run antivirus scan\n3. Clean temporary files\n4. Upgrade RAM if needed.',28,'2025-07-27 01:00:42');
/*!40000 ALTER TABLE `troubleshooting_docs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:30
