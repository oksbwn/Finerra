-- Auto-generated schema from SQLAlchemy models
-- Dialect: DuckDB (compatible with PostgreSQL syntax mostly)


CREATE TABLE tenants (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;


CREATE TABLE users (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	role userrole NOT NULL, 
	scopes VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id)
)

;


CREATE TABLE accounts (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	owner_id VARCHAR, 
	name VARCHAR NOT NULL, 
	type accounttype NOT NULL, 
	currency VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
)

;


CREATE TABLE transactions (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	account_id VARCHAR NOT NULL, 
	amount NUMERIC(15, 2) NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	description VARCHAR, 
	category VARCHAR, 
	tags VARCHAR, 
	external_id VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id), 
	FOREIGN KEY(account_id) REFERENCES accounts (id)
)

;

