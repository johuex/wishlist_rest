create table "users"
(
	"user_ID" integer not null
		constraint user_pk
			primary key,
	phone_number varchar(12) not null,
	user_name varchar(50) not null,
	surname varchar(50) not null,
	userpic bytea,
	about varchar(255),
	birthday date not null,
    password_hash varchar(255),
    nickname varchar(50) not null,
    email varchar(255) not null,
    last_seen timestamp
);
create unique index users_nickname_uindex
	on users (nickname);

create unique index users_email_uindex
	on users (email);

create sequence "users_user_ID_seq";

alter table users alter column "user_ID" set default nextval('public."users_user_ID_seq"');

alter sequence "users_user_ID_seq" owned by users."user_ID";

alter table users owner to dimas;

create table friendship
(
	"user_ID_1" int not null,
	"user_ID_2" int not null,
	constraint friendship_pk
		primary key ("user_ID_1", "user_ID_2"),
	constraint friendship_user_user_id_user_id_fk_1
		foreign key ("user_ID_1") references users ("user_ID")
			on update cascade on delete cascade,
	constraint friendship_user_user_id_user_id_fk_2
		foreign key ("user_ID_2") references users ("user_ID")
			on update cascade on delete cascade
);

create table wishlist
(
	list_id int not null
		constraint wishlist_pk
			primary key,
	"user_ID" int not null
		constraint wishlist_user_user_id_fk
			references users
				on update cascade on delete cascade,
	title varchar(50) not null,
	about varchar(255),
	access_level bool not null
);

create table group_wishlist
(
	"group_ID" int not null
		constraint group_wishlist_pk
			primary key,
	title varchar(255) not null,
	about varchar(255),
	date date not null
);

create table group_user
(
	"group_ID" int not null
		constraint group_user_group_wishlist_group_id_fk
			references group_wishlist
				on update cascade on delete cascade,
	"user_ID" int not null
		constraint group_user_user_user_id_fk
			references users
				on update cascade on delete cascade,
	role int not null,
	constraint group_user_pk
		primary key ("group_ID", "user_ID")
);

create table item
(
	"item_ID" int not null
		constraint item_pk
			primary key,
	title varchar(50) not null,
	about varchar(255) not null,
	access_level bool not null,
	picture bytea not null,
	"giver_ID" int
		constraint item_user_user_id_fk
			references users
				on update cascade on delete cascade
);

create table item_list
(
	"list_ID" int not null
		constraint item_list_wishlist_list_id_fk
			references wishlist
				on update cascade on delete cascade,
	"item_ID" int not null
		constraint item_list_item_item_id_fk
			references item
				on update cascade on delete cascade,
	constraint item_list_pk
		primary key ("list_ID", "item_ID")
);

create table status
(
	status varchar(50) not null
		constraint table_name_pk
			primary key
);

create table degree_of_desire
(
	degree varchar(50) not null
		constraint degree_of_desire_pk
			primary key
);

create table item_status
(
	"item_ID" int not null
		constraint item_status_item_item_id_fk
			references item
				on update cascade on delete cascade,
	status varchar(50) not null
		constraint item_status_status_status_fk
			references status
				on update cascade on delete cascade,
	constraint item_status_pk
		primary key ("item_ID", status)
);

create table item_degree
(
	"item_ID" int not null
		constraint item_degree_item_item_id_fk
			references item
				on update cascade on delete cascade,
	degree varchar(50) not null
		constraint item_degree_degree_of_desire_degree_fk
			references degree_of_desire
				on update cascade on delete cascade,
	constraint item_degree_pk
		primary key ("item_ID", degree)
);

create table user_item
(
	user_id int not null
		constraint user_item_users_user_id_fk
			references users
				on update cascade on delete cascade,
	item_id int not null
		constraint user_item_item_item_id_fk
			references item
				on update cascade on delete cascade,
	constraint user_item_pk
		primary key (item_id, user_id)
);




