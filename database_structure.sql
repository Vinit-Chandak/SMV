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
	Average_Temperature_Uncertainity numeric(5, 3) DEFAULT NULL,
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

END TRANSACTION;

