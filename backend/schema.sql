-- Auto-generated schema from SQLAlchemy models
-- Dialect: DuckDB (compatible with PostgreSQL syntax mostly)

CREATE TABLE tenants (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	role VARCHAR NOT NULL, 
	scopes VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);

CREATE TABLE accounts (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	owner_id VARCHAR, 
	name VARCHAR NOT NULL, 
	type VARCHAR NOT NULL, 
	currency VARCHAR NOT NULL, 
	account_mask VARCHAR,
	owner_name VARCHAR,
	balance NUMERIC(15, 2),
	is_verified BOOLEAN DEFAULT TRUE NOT NULL,
	import_config VARCHAR,
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
);

CREATE TABLE categories (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	icon VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);

CREATE TABLE transactions (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	account_id VARCHAR NOT NULL, 
	type VARCHAR NOT NULL DEFAULT 'DEBIT',
	amount NUMERIC(15, 2) NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	description VARCHAR, 
	recipient VARCHAR, 
	category VARCHAR, 
	tags VARCHAR, 
	external_id VARCHAR, 
	source VARCHAR NOT NULL DEFAULT 'MANUAL',
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id), 
	FOREIGN KEY(account_id) REFERENCES accounts (id)
);

CREATE TABLE category_rules (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	keywords VARCHAR NOT NULL, 
	priority NUMERIC(5, 0) DEFAULT 0, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);

CREATE TABLE budgets (
	id VARCHAR NOT NULL, 
	tenant_id VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	amount_limit NUMERIC(15, 2) NOT NULL, 
	period VARCHAR DEFAULT 'MONTHLY', 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);

