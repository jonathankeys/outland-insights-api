CREATE TABLE expedition_routes (
	id varchar(36) PRIMARY KEY,
	expedition_id varchar(36),
	name VARCHAR(255) NOT NULL,
	geojson jsonb,
	user_ids VARCHAR(36)[],
	names VARCHAR(255)[],
	created_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
	updated_at timestamp WITH time ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);