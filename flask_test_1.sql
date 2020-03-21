create database `flask_test_1` default character set utf8;
use `flask_test_1`;
create table `accounts` (
`id` int(11) not null auto_increment,
`username` varchar(50) not null,
`password` varchar(255) not null,
`email` varchar(100) not null,
`address` varchar(100),
`birthday` varchar(50),
primary key (`id`)
) auto_increment=1 default charset=utf8;