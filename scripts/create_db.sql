create table users
(
	id serial
		constraint users_pk
			primary key,
	phone_number varchar(20),
	user_name varchar(50) not null,
	surname varchar(50),
	userpic text,
	about varchar(1000),
	birthday date,
	password_hash text not null,
	nickname varchar(100) not null,
	email varchar(255) not null,
	token text,
	token_expiration timestamptz,
	last_seen timestamptz
);

create unique index users_email_uindex
	on users (email);

create unique index users_nickname_uindex
	on users (nickname);

create table wishlist
(
	id serial
		constraint wishlist_pk
			primary key,
	user_id int not null
		constraint wishlist_users_id_fk
			references users
				on update cascade on delete cascade,
	title varchar(50) not null,
	about varchar(255),
	access_level int not null
);

create table "group"
(
	id serial
		constraint group_pk
			primary key,
	title varchar(50) not null,
	about varchar(1000),
	date timestamptz not null
);

create table item
(
	id serial
		constraint item_pk
			primary key,
	title varchar(50) not null,
	about varchar(255),
	access_level int not null,
	status int not null,
	giver_id int
		constraint item_users_id_fk
			references users
				on update cascade on delete cascade,
	date_creation date not null,
	date_for_status date
);

create table friend_requests
(
	user_id_from int
		constraint friend_requests_users_id_fk
			references users
				on update cascade on delete cascade,
	user_id_to int
		constraint friend_requests_users_id_fk_2
			references users
				on update cascade on delete cascade,
	constraint friend_requests_pk
		primary key (user_id_from, user_id_to)
);

create table friendship
(
	user_id_1 int
		constraint friendship_users_id_fk
			references users
				on update cascade on delete cascade,
	user_id_2 int
		constraint friendship_users_id_fk_2
			references users
				on update cascade on delete cascade,
	constraint friendship_pk
		primary key (user_id_1, user_id_2)
);

create table user_item
(
	user_id int
		constraint user_item_users_id_fk
			references users
				on update cascade on delete cascade,
	item_id int
		constraint user_item_item_id_fk
			references item
				on update cascade on delete cascade,
	constraint user_item_pk
		primary key (user_id, item_id)
);

create table item_list
(
	list_id int
		constraint item_list_wishlist_id_fk
			references wishlist
				on update cascade on delete cascade,
	item_id int
		constraint item_list_item_id_fk
			references item
				on update cascade on delete cascade,
	constraint item_list_pk
		primary key (list_id, item_id)
);

create table group_list
(
	group_id int
		constraint group_list_group_id_fk
			references "group"
				on update cascade on delete cascade,
	list_id int
		constraint group_list_wishlist_id_fk
			references wishlist
				on update cascade on delete cascade,
	constraint group_list_pk
		primary key (group_id, list_id)
);

create table group_user
(
	group_id int
		constraint group_user_group_id_fk
			references "group"
				on update cascade on delete cascade,
	user_id int
		constraint group_user_users_id_fk
			references users
				on update cascade on delete cascade,
	role_in_group int,
	constraint group_user_pk
		primary key (group_id, user_id)
);

create table degree_of_desire
(
	item_id int
		constraint degree_of_desire_pk
			primary key
		constraint degree_of_desire_item_id_fk
			references item
				on update cascade on delete cascade,
	degree varchar(50) not null
);

create table item_picture
(
	item_id int
		constraint item_picture_pk
			primary key
		constraint item_picture_item_id_fk
			references item
				on update cascade on delete cascade,
	path_to_picture int not null
);

create table item_group
(
	group_id int
		constraint item_group_group_id_fk
			references "group"
				on update cascade on delete cascade,
	item_id int
		constraint item_group_item_id_fk
			references item
				on update cascade on delete cascade,
	constraint item_group_pk
		primary key (item_id, group_id)
);
