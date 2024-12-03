CREATE DATABASE billing_db;

\c billing_db;

CREATE TYPE subscription_status AS ENUM ('active', 'cancelled', 'expired');
CREATE TYPE transaction_status AS ENUM ('pending', 'succeeded', 'failed');
CREATE TYPE transaction_type AS ENUM ('subscription', 'movie');
CREATE TYPE purchase_status AS ENUM ('paid', 'failed');
CREATE TYPE discount_type AS ENUM ('percentage', 'fixed');


CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    subscription_id UUID NOT NULL,
    status subscription_status NOT NULL,
    next_billing_date TIMESTAMP,
    payment_method_id UUID
);


CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    base_currency VARCHAR(3) NOT NULL
);


CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status transaction_status NOT NULL,
    type transaction_type NOT NULL,
    subscription_id UUID REFERENCES subscriptions(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);


CREATE TABLE film_purchases (
    purchase_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    movie_id UUID NOT NULL,
    status purchase_status NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE discounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    type discount_type NOT NULL,
    value DECIMAL(5, 2) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL
);


CREATE TABLE film_prices (
    id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL
);
