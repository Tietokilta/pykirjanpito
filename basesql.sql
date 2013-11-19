-- phpMyAdmin SQL Dump
-- version 3.5.8.1deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 19, 2013 at 03:00 PM
-- Server version: 5.5.34-0ubuntu0.13.04.1
-- PHP Version: 5.4.9-4ubuntu2.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `kirjanpito`
--

-- --------------------------------------------------------

--
-- Table structure for table `event`
--

CREATE TABLE IF NOT EXISTS `event` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `regular_expression` varchar(255) DEFAULT NULL,
  `keyword` varchar(255) NOT NULL,
  `price` decimal(15,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=12 ;

-- --------------------------------------------------------

--
-- Table structure for table `order`
--

CREATE TABLE IF NOT EXISTS `order` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `is_paid` tinyint(1) NOT NULL DEFAULT '0',
  `paid_date` date DEFAULT NULL,
  `payment` decimal(16,2) DEFAULT NULL,
  `requested_payment` decimal(16,2) DEFAULT NULL,
  `comments` text,
  `event_id` int(10) DEFAULT NULL,
  `last_checked` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=380 ;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `order`
--
ALTER TABLE `order`
  ADD CONSTRAINT `order_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
