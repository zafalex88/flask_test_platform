use `flask_test_1`;
create table `followers` (
`id` int(11) not null auto_increment primary key,
`follower_id` int(11),
`followed_id` int(11),
`followed_username` varchar(50),
foreign key (`followed_username`) references accounts(`username`),
foreign key (`follower_id`) references accounts(`id`),
foreign key (`followed_id`) references accounts(`id`)
) auto_increment=1 default charset=utf8;