CREATE TABLE users (
	id varchar(36) PRIMARY KEY,
	first_name varchar(255) NOT NULL,
	last_name varchar(255) NOT NULL,
	email varchar(255) NOT NULL UNIQUE,
	created_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	updated_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE UNIQUE index users_emailx ON users (email);