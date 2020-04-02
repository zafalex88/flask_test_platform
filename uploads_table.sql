use `flask_test_1`;
create table `uploads` (
`id` int(11) not null auto_increment primary key,
`uploader_id` int(11),
`recipes` text,
`photos` longblob,
foreign key (`uploader_id`) references accounts(`id`)
) auto_increment=1 default charset=utf8;