CREATE TABLE user_passwords (
	user_id VARCHAR(36) PRIMARY KEY,
	password VARCHAR(255) NOT NULL,
	created_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	updated_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);