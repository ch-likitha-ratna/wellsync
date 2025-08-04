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
-- Table structure for table `asset_inventory`
--

DROP TABLE IF EXISTS `asset_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asset_inventory` (
  `asset_id` int NOT NULL AUTO_INCREMENT,
  `asset_name` varchar(100) NOT NULL,
  `asset_type` enum('Laptop','Desktop','Monitor','Keyboard','Mouse','Headset','Other') NOT NULL,
  `serial_number` varchar(100) NOT NULL,
  `purchase_date` date DEFAULT NULL,
  `assigned_to` int DEFAULT NULL,
  `status` enum('In Use','Available','Under Repair','Retired') DEFAULT 'Available',
  PRIMARY KEY (`asset_id`),
  UNIQUE KEY `serial_number` (`serial_number`),
  KEY `assigned_to` (`assigned_to`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asset_inventory`
--

LOCK TABLES `asset_inventory` WRITE;
/*!40000 ALTER TABLE `asset_inventory` DISABLE KEYS */;
INSERT INTO `asset_inventory` VALUES (1,'MacBook Pro 16\"','Laptop','SN-MBP2023-001','2023-01-15',5,'In Use'),(2,'Dell XPS 15','Laptop','SN-DXPS2023-002','2023-02-20',7,'In Use'),(3,'iPad Pro 12.9\"','Other','SN-IPAD2023-003','2023-03-10',3,'In Use'),(4,'iPhone 14 Pro','Other','SN-IPH2023-004','2023-04-05',4,'In Use'),(5,'Samsung Galaxy S23','Other','SN-SGS2023-005','2023-05-12',8,'In Use'),(6,'Lenovo ThinkPad','Laptop','SN-LTP2023-006','2023-06-18',9,'In Use'),(7,'Canon Printer','Other','SN-CP2023-007','2023-07-22',NULL,'Available'),(8,'Conference Room Monitor','Monitor','SN-CRM2023-008','2023-08-30',NULL,'Available'),(9,'Apple Watch','Other','SN-AW2023-009','2023-09-15',2,'In Use'),(10,'Noise-Canceling Headphones','Headset','SN-HP2023-010','2023-10-10',6,'In Use');
/*!40000 ALTER TABLE `asset_inventory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:38
