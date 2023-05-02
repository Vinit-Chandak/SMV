BEGIN TRANSACTION;

DROP TABLE IF EXISTS States;
CREATE TABLE States(
    State varchar(30),
    Capital varchar(30) NOT NULL,
    PRIMARY KEY (State)
);

DROP TABLE IF EXISTS Cities;
CREATE TABLE Cities(
    City varchar(30),
    State varchar(30),
    PRIMARY KEY (City, State),
    FOREIGN KEY (State)
        REFERENCES States(State)
        DEFERRABLE INITIALLY DEFERRED
);

ALTER TABLE States
ADD CONSTRAINT fk_capital
    FOREIGN KEY (Capital, State)
        REFERENCES Cities (City, State)
        DEFERRABLE INITIALLY DEFERRED;


DROP TABLE IF EXISTS State_Subdivision;
CREATE TABLE State_Subdivision(
	State varchar(30),
	Subdivision varchar(50),
	FOREIGN KEY(State)
	REFERENCES States(State)
	ON DELETE CASCADE,
	Primary Key(Subdivision)
);

DROP TABLE IF EXISTS State_CO2;
CREATE TABLE State_CO2(
	State varchar(30),
	Year int,
	CO2_Emissions numeric(10,2) DEFAULT NULL,
	FOREIGN KEY(State)
	REFERENCES States(State)
	ON DELETE CASCADE,
	PRIMARY KEY(State, Year)
);

DROP TABLE IF EXISTS Average_Temoerature;
CREATE TABLE Average_Temperature(
	Average_Temperature numeric(6, 3) DEFAULT NULL,
	Average_Temperature_Uncertainty numeric(5, 3) DEFAULT NULL,
	State varchar(30),
	Month varchar(15),
	Year int,
	FOREIGN KEY(State)
	REFERENCES States(State)
	ON DELETE CASCADE,
	PRIMARY KEY(State, Month, Year)
);

DROP TABLE IF EXISTS CO2;
CREATE TABLE CO2(
	Year int NOT NULL,
	Population numeric(10) DEFAULT NULL,
	Gdp numeric(14) DEFAULT NULL,
	cement_co2_per_capita numeric(10,3) DEFAULT NULL,
	Co2_including_luc_per_capita numeric(10,3) DEFAULT NULL,
	Co2_per_capita numeric(10,3) DEFAULT NULL,
	Coal_co2_per_capita numeric(10,3) DEFAULT NULL,
	Consumption_co2_per_capita numeric(10,3) DEFAULT NULL,
	Energy_per_capita numeric(10,3) DEFAULT NULL,
	Flaring_co2_per_capita numeric(10,3) DEFAULT NULL,
	Gas_co2_per_capita numeric(10,3) DEFAULT NULL,
	Ghg_excluding_lucf_per_capita numeric(10,3) DEFAULT NULL,
	Ghg_per_capita numeric(10,3) DEFAULT NULL,
	Land_use_change_co2_per_capita numeric(10,3) DEFAULT NULL,
	PRIMARY KEY( Year)
);


DROP TABLE IF EXISTS Sealevel;
CREATE TABLE Sealevel(
	State varchar(30),
	Sea_Shore_City varchar(30),
	Year int NOT NULL,
	Month varchar(20) NOT NULL,
	Monthly_MSL numeric(4, 3) DEFAULT NULL,
	Linear_Trend numeric(4, 3) DEFAULT NULL,
	High_Conf numeric(4, 3) DEFAULT NULL,
	Low_Conf numeric(4, 3) DEFAULT NULL,
	FOREIGN KEY(Sea_Shore_City, State)
	REFERENCES Cities(City, State)
	ON DELETE CASCADE,
	PRIMARY KEY(State, Sea_Shore_City, Year, Month)
);


DROP TABLE IF EXISTS Rainfall;
CREATE TABLE Rainfall(
	Subdivision varchar(50),
	Year int NOT NULL,
	January numeric(5,1) DEFAULT NULL,
	February numeric(5,1) DEFAULT NULL,
	March numeric(5,1) DEFAULT NULL,
	April numeric(5,1) DEFAULT NULL,
	May numeric(5,1) DEFAULT NULL,
	June numeric(5,1) DEFAULT NULL,
	July numeric(5,1) DEFAULT NULL,
	August  numeric(5,1) DEFAULT NULL,
	September numeric(5,1) DEFAULT NULL,
	October numeric(5,1) DEFAULT NULL,
	November numeric(5,1) DEFAULT NULL,
	December numeric(5,1) DEFAULT NULL,
	Annual numeric(5, 1) DEFAULT NULL,
	January_February numeric(5,1) DEFAULT NULL,
	March_May numeric(5,1) DEFAULT NULL,
	June_September numeric(5,1) DEFAULT NULL,
	October_December numeric(5,1) DEFAULT NULL,
	PRIMARY KEY(Subdivision, Year),
	FOREIGN KEY(Subdivision)
	REFERENCES State_Subdivision(Subdivision)
	ON DELETE CASCADE
);


DROP TABLE IF EXISTS AQI;
CREATE TABLE AQI(
	City varchar(30),
	State varchar(30),
	Date date NOT NULL,
	PM2_5 numeric(5,2) DEFAULT NULL,
	PM10 numeric(5,2) DEFAULT NULL,
	AQI int DEFAULT NULL,
	AQI_Bucket varchar(30) DEFAULT NULL,
	PRIMARY KEY(City, State, Date),
	FOREIGN KEY(City, State)
	REFERENCES Cities(City, State)
	ON DELETE CASCADE
);

DROP TABLE IF EXISTS weather_alerts;
CREATE TABLE weather_alerts (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  state VARCHAR(255) NOT NULL,
  city VARCHAR(255) NOT NULL
);


CREATE INDEX idx_state_subdivision_subdivision_state ON state_subdivision(subdivision, state);

CREATE INDEX avg_temp_state_idx on average_temperature(state);
CREATE INDEX avg_temp_year_idx on average_temperature(year);
CREATE INDEX avg_temp_state_year_idx on average_temperature(state, year);

CREATE INDEX rainfall_subdiv_idx on rainfall(subdivision);
CREATE INDEX rainfall_year_idx on rainfall(year);
CREATE INDEX rainfall_state_year_idx on rainfall(subdivision, year);
CREATE INDEX idx_rainfall_subdivision_annual_year ON rainfall(subdivision, annual, year);

CREATE INDEX state_co2_state_idx ON state_co2(state);
CREATE INDEX state_co2_year_idx ON state_co2(year);
CREATE INDEX state_co2_state_year_idx ON state_co2(state, year);

CREATE INDEX sealevel_state_idx ON sealevel(state);
CREATE INDEX sealevel_year_idx ON sealevel(year);
CREATE INDEX sealevel_city_idx ON sealevel(sea_shore_city);
CREATE INDEX idx_sealevel_state_year_monthly_msl ON sealevel(state, year, monthly_msl);

CREATE INDEX aqi_state_idx ON aqi(state);
CREATE INDEX aqi_city_idx ON aqi(city);
CREATE INDEX aqi_date_idx ON aqi(date);

CREATE INDEX co2_year_idx ON co2(year);
CREATE INDEX co2_per_capita_idx ON co2(Co2_per_capita);

CREATE OR REPLACE FUNCTION check_valid_temperature()
RETURNS TRIGGER AS $$
BEGIN
IF NEW.Average_Temperature < -273.15 THEN
	RAISE EXCEPTION 'Invalid temperature value: below absolute zero.';
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_valid_temperature
BEFORE INSERT OR UPDATE ON Average_Temperature
FOR EACH ROW
EXECUTE PROCEDURE check_valid_temperature();

CREATE OR REPLACE FUNCTION update_state_capital()
RETURNS TRIGGER AS $$
BEGIN
-- Check if the capital has changed
IF OLD.Capital <> NEW.Capital THEN
	-- Update the capital in the Cities table
	UPDATE Cities
	SET City = NEW.Capital
	WHERE City = OLD.Capital
	AND State = NEW.State;

	-- Update the capital in the Sealevel table
	UPDATE Sealevel
	SET Sea_Shore_City = NEW.Capital
	WHERE Sea_Shore_City = OLD.Capital
	AND State = NEW.State;
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_state_capital
AFTER UPDATE ON States
FOR EACH ROW
EXECUTE PROCEDURE update_state_capital();

CREATE OR REPLACE FUNCTION calculate_annual_quarterly_rainfall()
RETURNS TRIGGER AS $$
BEGIN
	-- Calculate Annual rainfall
	NEW.Annual = COALESCE(NEW.January, 0) + COALESCE(NEW.February, 0) + COALESCE(NEW.March, 0) + COALESCE(NEW.April, 0)
				+ COALESCE(NEW.May, 0) + COALESCE(NEW.June, 0) + COALESCE(NEW.July, 0) + COALESCE(NEW.August, 0)
				+ COALESCE(NEW.September, 0) + COALESCE(NEW.October, 0) + COALESCE(NEW.November, 0) + COALESCE(NEW.December, 0);

	-- Calculate quarterly rainfall
	NEW.January_February = COALESCE(NEW.January, 0) + COALESCE(NEW.February, 0);
	NEW.March_May = COALESCE(NEW.March, 0) + COALESCE(NEW.April, 0) + COALESCE(NEW.May, 0);
	NEW.June_September = COALESCE(NEW.June, 0) + COALESCE(NEW.July, 0) + COALESCE(NEW.August, 0) + COALESCE(NEW.September, 0);
	NEW.October_December = COALESCE(NEW.October, 0) + COALESCE(NEW.November, 0) + COALESCE(NEW.December, 0);

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_annual_quarterly_rainfall
BEFORE INSERT OR UPDATE ON Rainfall
FOR EACH ROW
EXECUTE PROCEDURE calculate_annual_quarterly_rainfall();

CREATE TABLE average_temperature_audit (
	audit_id SERIAL PRIMARY KEY,
	operation VARCHAR(10) NOT NULL,
	state VARCHAR(30),
	month VARCHAR(15),
	year INT,
	old_avg_temperature NUMERIC(6, 3),
	new_avg_temperature NUMERIC(6, 3),
	old_avg_temperature_uncertainty NUMERIC(5, 3),
	new_avg_temperature_uncertainty NUMERIC(5, 3),
	changed_by VARCHAR(100) NOT NULL,
	changed_at TIMESTAMP NOT NULL
);

CREATE OR REPLACE FUNCTION average_temperature_audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
	IF TG_OP = 'UPDATE' THEN
		INSERT INTO average_temperature_audit (
			operation, state, month, year,
			old_avg_temperature, new_avg_temperature,
			old_avg_temperature_uncertainty, new_avg_temperature_uncertainty,
			changed_by, changed_at
		)
		VALUES (
			'UPDATE', NEW.state, NEW.month, NEW.year,
			OLD.average_temperature, NEW.average_temperature,
			OLD.average_temperature_uncertainty, NEW.average_temperature_uncertainty,
			current_user, current_timestamp
		);
		RETURN NEW;
	ELSIF TG_OP = 'DELETE' THEN
		INSERT INTO average_temperature_audit (
			operation, state, month, year,
			old_avg_temperature, new_avg_temperature,
			old_avg_temperature_uncertainty, new_avg_temperature_uncertainty,
			changed_by, changed_at
		)
		VALUES (
			'DELETE', OLD.state, OLD.month, OLD.year,
			OLD.average_temperature, NULL,
			OLD.average_temperature_uncertainty, NULL,
			current_user, current_timestamp
		);
		RETURN OLD;
	ELSIF TG_OP = 'INSERT' THEN
		INSERT INTO average_temperature_audit (
			operation, state, month, year,
			old_avg_temperature, new_avg_temperature,
			old_avg_temperature_uncertainty, new_avg_temperature_uncertainty,
			changed_by, changed_at
		)
		VALUES (
			'INSERT', NEW.state, NEW.month, NEW.year,
			NULL, NEW.average_temperature,
			NULL, NEW.average_temperature_uncertainty,
			current_user, current_timestamp
		);
		RETURN NEW;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER average_temperature_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON average_temperature
FOR EACH ROW
EXECUTE PROCEDURE average_temperature_audit_trigger_func();

END TRANSACTION;

