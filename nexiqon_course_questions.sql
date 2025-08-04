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
-- Table structure for table `course_questions`
--

DROP TABLE IF EXISTS `course_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_questions` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int DEFAULT NULL,
  `question_text` text NOT NULL,
  `option_a` varchar(500) NOT NULL,
  `option_b` varchar(500) NOT NULL,
  `option_c` varchar(500) NOT NULL,
  `option_d` varchar(500) NOT NULL,
  `correct_answer` enum('A','B','C','D') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`question_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `course_questions_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course_catalog` (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_questions`
--

LOCK TABLES `course_questions` WRITE;
/*!40000 ALTER TABLE `course_questions` DISABLE KEYS */;
INSERT INTO `course_questions` VALUES (21,4,'What is the correct way to create a list in Python?','list = []','list = ()','list = {}','list = \"\"','A','2025-07-28 14:25:50'),(22,4,'Which keyword is used to define a function in Python?','function','def','func','define','B','2025-07-28 14:25:50'),(23,4,'What does the len() function return?','The length of an object','The last element','The first element','The type of object','A','2025-07-28 14:25:50'),(24,4,'How do you create a comment in Python?','// This is a comment','/* This is a comment */','# This is a comment','<!-- This is a comment -->','C','2025-07-28 14:25:50'),(25,4,'Which of the following is a mutable data type?','tuple','string','list','int','C','2025-07-28 14:25:50'),(26,4,'What is the output of print(2 ** 3)?','5','6','8','9','C','2025-07-28 14:25:50'),(27,4,'How do you import a module named \"math\"?','include math','import math','using math','require math','B','2025-07-28 14:25:50'),(28,4,'What is the correct way to create a dictionary?','dict = []','dict = ()','dict = {}','dict = \"\"','C','2025-07-28 14:25:50'),(29,4,'Which method adds an element to a list?','add()','append()','insert()','push()','B','2025-07-28 14:25:50'),(30,4,'What is the result of \"Hello\" + \"World\"?','Hello World','HelloWorld','Hello+World','Error','B','2025-07-28 14:25:50'),(31,4,'How do you create a for loop in Python?','for i in range(10):','for (i=0; i<10; i++):','for i = 1 to 10:','foreach i in 10:','A','2025-07-28 14:25:50'),(32,4,'What does range(5) generate?','1, 2, 3, 4, 5','0, 1, 2, 3, 4','0, 1, 2, 3, 4, 5','1, 2, 3, 4','B','2025-07-28 14:25:50'),(33,4,'Which operator is used for floor division?','/','//','%','**','B','2025-07-28 14:25:50'),(34,4,'How do you handle exceptions in Python?','try-catch','try-except','try-finally','catch-throw','B','2025-07-28 14:25:50'),(35,4,'What converts a string to lowercase?','toLower()','lower()','lowercase()','downcase()','B','2025-07-28 14:25:50'),(36,4,'How do you create a class in Python?','class MyClass:','def MyClass:','create MyClass:','new MyClass:','A','2025-07-28 14:25:50'),(37,4,'What is the purpose of __init__ method?','To destroy objects','To initialize objects','To copy objects','To compare objects','B','2025-07-28 14:25:50'),(38,4,'Which statement exits a loop prematurely?','exit','break','stop','end','B','2025-07-28 14:25:50'),(39,4,'What does strip() method do?','Removes whitespace from both ends','Converts to uppercase','Splits the string','Reverses the string','A','2025-07-28 14:25:50'),(40,4,'How do you check if a key exists in dictionary?','key in dict','dict.hasKey(key)','dict.contains(key)','key.exists(dict)','A','2025-07-28 14:25:50'),(41,5,'Primary library for data manipulation in Python?','NumPy','Pandas','Matplotlib','Scikit-learn','B','2025-07-28 14:25:50'),(42,5,'Which measure is most affected by outliers?','Mean','Median','Mode','Range','A','2025-07-28 14:25:50'),(43,5,'What does CSV stand for?','Computer Separated Values','Comma Separated Values','Character Separated Values','Column Separated Values','B','2025-07-28 14:25:50'),(44,5,'Best plot for showing distribution of single variable?','Scatter plot','Line plot','Histogram','Bar plot','C','2025-07-28 14:25:50'),(45,5,'Purpose of data normalization?','Remove duplicates','Scale features to similar ranges','Sort data','Encrypt data','B','2025-07-28 14:25:50'),(46,5,'Algorithm used for classification problems?','Linear Regression','K-Means','Decision Tree','PCA','C','2025-07-28 14:25:50'),(47,5,'What does SQL stand for?','Structured Query Language','Simple Query Language','Standard Query Language','Sequential Query Language','A','2025-07-28 14:25:50'),(48,5,'Perfect positive correlation coefficient?','0','1','-1','0.5','B','2025-07-28 14:25:50'),(49,5,'What is overfitting in machine learning?','Model performs well on training but poorly on test','Model performs poorly on both','Model performs well on both','Model cannot be trained','A','2025-07-28 14:25:50'),(50,5,'Common machine learning library in Python?','Pandas','Matplotlib','Scikit-learn','Requests','C','2025-07-28 14:25:50'),(51,5,'Purpose of cross-validation?','Clean data','Evaluate model performance','Visualize data','Collect data','B','2025-07-28 14:25:50'),(52,5,'Test to compare means of two groups?','Chi-square test','t-test','ANOVA','Regression','B','2025-07-28 14:25:50'),(53,5,'What is a p-value?','Probability of observing results given null hypothesis','Percentage of variance explained','Prediction accuracy','Population parameter','A','2025-07-28 14:25:50'),(54,5,'Best data type for categorical variables?','Integer','Float','String','Boolean','C','2025-07-28 14:25:50'),(55,5,'Difference between supervised and unsupervised learning?','Supervised uses labeled data, unsupervised does not','Supervised is faster','Supervised uses more data','No difference','A','2025-07-28 14:25:50'),(56,5,'Technique for dimensionality reduction?','PCA','Linear Regression','Decision Tree','K-Means','A','2025-07-28 14:25:50'),(57,5,'Purpose of feature engineering?','Create new features from existing ones','Remove all features','Visualize features','Encrypt features','A','2025-07-28 14:25:50'),(58,5,'Metric to evaluate classification models?','R-squared','Mean Squared Error','Accuracy','Mean Absolute Error','C','2025-07-28 14:25:50'),(59,5,'What is a confusion matrix?','Table showing prediction vs actual results','Correlation matrix','Data cleaning tool','Visualization technique','A','2025-07-28 14:25:50'),(60,5,'Algorithm used for clustering?','Linear Regression','Decision Tree','K-Means','Logistic Regression','C','2025-07-28 14:25:50'),(61,6,'What does HTML stand for?','Hyper Text Markup Language','High Tech Modern Language','Home Tool Markup Language','Hyperlink and Text Markup Language','A','2025-07-28 14:25:50'),(62,6,'HTML tag for largest heading?','<h6>','<h1>','<header>','<head>','B','2025-07-28 14:25:50'),(63,6,'What does CSS stand for?','Cascading Style Sheets','Computer Style Sheets','Creative Style Sheets','Colorful Style Sheets','A','2025-07-28 14:25:50'),(64,6,'CSS property to change text color?','text-color','color','font-color','text-style','B','2025-07-28 14:25:50'),(65,6,'HTML tag for line break?','<break>','<br>','<lb>','<newline>','B','2025-07-28 14:25:50'),(66,6,'JavaScript method to write HTML output?','document.write()','console.log()','window.alert()','document.print()','A','2025-07-28 14:25:50'),(67,6,'How to create function in JavaScript?','function myFunction()','create myFunction()','def myFunction()','function = myFunction()','A','2025-07-28 14:25:50'),(68,6,'HTML attribute for alternate text for image?','title','alt','src','longdesc','B','2025-07-28 14:25:50'),(69,6,'CSS syntax for making <p> elements bold?','p {text-size: bold;}','p {font-weight: bold;}','p {text-style: bold;}','p {font-style: bold;}','B','2025-07-28 14:25:50'),(70,6,'HTML tag for internal style sheet?','<css>','<script>','<style>','<link>','C','2025-07-28 14:25:50'),(71,6,'Select element with id \"demo\" in CSS?','.demo','#demo','demo','*demo','B','2025-07-28 14:25:50'),(72,6,'JavaScript event for user click?','onchange','onclick','onmouseclick','onmouseover','B','2025-07-28 14:25:50'),(73,6,'Correct HTML for hyperlink?','<a url=\"http://example.com\">Example</a>','<a href=\"http://example.com\">Example</a>','<a>http://example.com</a>','<a name=\"http://example.com\">Example</a>','B','2025-07-28 14:25:50'),(74,6,'CSS property for background color?','bgcolor','background-color','color','bg-color','B','2025-07-28 14:25:50'),(75,6,'Add comment in JavaScript?','<!-- comment -->','// comment','# comment','/* comment */','B','2025-07-28 14:25:50'),(76,6,'HTML tag to define table?','<table>','<tab>','<tr>','<td>','A','2025-07-28 14:25:50'),(77,6,'Include external CSS file?','<link rel=\"stylesheet\" href=\"style.css\">','<style src=\"style.css\">','<css>style.css</css>','<include>style.css</include>','A','2025-07-28 14:25:50'),(78,6,'JavaScript operator to assign value?','*','=','-','x','B','2025-07-28 14:25:50'),(79,6,'Create array in JavaScript?','var colors = \"red\", \"green\"','var colors = (1:\"red\", 2:\"green\")','var colors = [\"red\", \"green\"]','var colors = 1 = (\"red\")','C','2025-07-28 14:25:50'),(80,6,'HTML attribute for inline styles?','class','style','styles','font','B','2025-07-28 14:25:50');
/*!40000 ALTER TABLE `course_questions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-02  7:13:39
