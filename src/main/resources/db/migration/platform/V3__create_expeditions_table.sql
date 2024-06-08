CREATE TABLE expeditions (
	id varchar(36) PRIMARY KEY,
	name varchar(255) NOT NULL,
	description TEXT,
	image_url varchar(255),
	organization_id varchar(36),
	user_id varchar(36),
	start_time timestamp with time zone not null DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	end_time timestamp with time zone not null DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	created_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	updated_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

ALTER TABLE expeditions ADD CONSTRAINT fk_organization_id
FOREIGN KEY(organization_id)
REFERENCES organizations(id);

ALTER TABLE expeditions ADD CONSTRAINT fk_user_id
FOREIGN KEY(user_id)
REFERENCES users(id);

ALTER TABLE expeditions ADD CONSTRAINT non_null_organization_or_user
CHECK ((organization_id IS NOT NULL OR user_id IS NULL) OR (organization_id IS NULL OR user_id IS NOT NULL));