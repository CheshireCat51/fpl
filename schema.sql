-- MySQL dump 10.13  Distrib 8.0.35, for Win64 (x86_64)
--
-- Host: localhost    Database: fpl_model_2425
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `gameweek`
--

DROP TABLE IF EXISTS `gameweek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gameweek` (
  `id` int NOT NULL,
  `deadline` datetime DEFAULT NULL,
  `is_current` tinyint(1) DEFAULT NULL,
  `my_projected_points` float DEFAULT NULL,
  `my_points_scored` float DEFAULT NULL,
  `mean_points_scored` int DEFAULT NULL,
  `mean_player_points_delta` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `my_team`
--

DROP TABLE IF EXISTS `my_team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_team` (
  `id` int NOT NULL AUTO_INCREMENT,
  `player_id` int NOT NULL,
  `is_captain` tinyint(1) DEFAULT NULL,
  `is_vice_captain` tinyint(1) DEFAULT NULL,
  `is_benched` int DEFAULT NULL,
  `purchase_price` float DEFAULT NULL,
  `selling_price` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player` (
  `id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `squad_id` int NOT NULL,
  `position` enum('GKP','DEF','MID','FWD') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `matches_played` int DEFAULT NULL,
  `minutes_played` int DEFAULT NULL,
  `goals` int DEFAULT NULL,
  `assists` int DEFAULT NULL,
  `penalty_goals` int DEFAULT NULL,
  `penalty_attempts` int DEFAULT NULL,
  `yellow_cards` int DEFAULT NULL,
  `red_cards` int DEFAULT NULL,
  `xG` float DEFAULT NULL,
  `npxG` float DEFAULT NULL,
  `xA` float DEFAULT NULL,
  `progressive_carries` int DEFAULT NULL,
  `progressive_passes` int DEFAULT NULL,
  `goals_per_90` float DEFAULT NULL,
  `assists_per_90` float DEFAULT NULL,
  `xG_per_90` float DEFAULT NULL,
  `npxG_per_90` float DEFAULT NULL,
  `xA_per_90` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player_gameweek`
--

DROP TABLE IF EXISTS `player_gameweek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_gameweek` (
  `id` int NOT NULL AUTO_INCREMENT,
  `player_id` int NOT NULL,
  `gameweek_id` int NOT NULL,
  `squad_gameweek_id` int DEFAULT NULL,
  `started` tinyint(1) DEFAULT NULL,
  `minutes_played` int DEFAULT NULL,
  `goals` int DEFAULT NULL,
  `assists` int DEFAULT NULL,
  `penalty_goals` int DEFAULT NULL,
  `penalty_attempts` int DEFAULT NULL,
  `yellow_cards` int DEFAULT NULL,
  `red_cards` int DEFAULT NULL,
  `xG` float DEFAULT NULL,
  `npxG` float DEFAULT NULL,
  `xA` float DEFAULT NULL,
  `xMins` float DEFAULT NULL,
  `projected_points` float DEFAULT NULL,
  `points_scored` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50094 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `squad`
--

DROP TABLE IF EXISTS `squad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `squad` (
  `id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `matches_played` int DEFAULT NULL,
  `goals` int DEFAULT NULL,
  `assists` int DEFAULT NULL,
  `penalty_goals` int DEFAULT NULL,
  `penalty_attempts` int DEFAULT NULL,
  `yellow_cards` int DEFAULT NULL,
  `red_cards` int DEFAULT NULL,
  `xG` float DEFAULT NULL,
  `xA` float DEFAULT NULL,
  `npxG` float DEFAULT NULL,
  `progressive_carries` int DEFAULT NULL,
  `progressive_passes` int DEFAULT NULL,
  `goals_per_90` float DEFAULT NULL,
  `assists_per_90` float DEFAULT NULL,
  `xG_per_90` float DEFAULT NULL,
  `xA_per_90` float DEFAULT NULL,
  `npxG_per_90` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `squad_gameweek`
--

DROP TABLE IF EXISTS `squad_gameweek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `squad_gameweek` (
  `id` int NOT NULL AUTO_INCREMENT,
  `squad_id` int NOT NULL,
  `gameweek_id` int NOT NULL,
  `opposition_id` int NOT NULL,
  `venue` enum('Home','Away','Neutral') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'Home',
  `overall_strength` float DEFAULT NULL,
  `attack_strength` float DEFAULT NULL,
  `defence_strength` float DEFAULT NULL,
  `xG` float DEFAULT NULL,
  `xGC` float DEFAULT NULL,
  `goals_scored` float DEFAULT NULL,
  `goals_conceded` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1521 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-23 11:22:03
