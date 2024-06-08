CREATE TABLE organizations (
	id varchar(36) PRIMARY KEY,
	name varchar(255) NOT NULL,
	description TEXT,
	image_url varchar(255),
	created_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	updated_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);