-- 1. Create Database
CREATE DATABASE IF NOT EXISTS world_debt_analytics;
USE world_debt_analytics;

-- 2. Countries Dimension Table
CREATE TABLE IF NOT EXISTS dim_countries (
    country_code VARCHAR(10) PRIMARY KEY,
    country_name VARCHAR(150) NOT NULL,
    region VARCHAR(100),
    income_group VARCHAR(100),
    currency_unit VARCHAR(100)
);

-- 3. Indicators Dimension Table
CREATE TABLE IF NOT EXISTS dim_indicators (
    series_code VARCHAR(50) PRIMARY KEY,
    series_name VARCHAR(255) NOT NULL,
    topic VARCHAR(255),
    source TEXT
);

-- 4. Central Debt Fact Table
CREATE TABLE IF NOT EXISTS fact_debt_data (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    series_code VARCHAR(50) NOT NULL,
    year SMALLINT NOT NULL,
    debt_value DOUBLE NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code) ON DELETE CASCADE,
    FOREIGN KEY (series_code) REFERENCES dim_indicators(series_code) ON DELETE CASCADE,
    INDEX idx_country_year (country_code, year),
    INDEX idx_series_year (series_code, year)
);