--Queries are with demo values, we would fetch the actual values form the frontend based on the user input--
--We might not use all of these queries in the final project, but we have included them for reference--
--Also, we might add new queries or slightly modify the existing ones in the future as needed--

--Average Temperature:--
	--To populate dropdown options--
		SELECT DISTINCT state FROM average_temperature;
		SELECT DISTINCT year FROM average_temperature WHERE state = 'Maharashtra';
		with month_to_num(month, num) AS (SELECT month, case when month='January' then 1 else case when month = 'February' then 2 else case when month = 'March' then 3 else case when month = 'April' then 4 else case when month = 'May' then 5 else case when month = 'June' then 6 else case when month = 'July' then 7 else case when month = 'August' then 8 else case when month = 'September' then 9 else case when month = 'October' then 10 else case when month = 'November' then 11 else case when month = 'December' then 12 end end end end end end end end end end end end AS num FROM average_temperature ORDER BY num),
		sorted(month) AS (SELECT DISTINCT average_temperature.month, num FROM average_temperature, month_to_num WHERE state = 'Maharashtra' and year = '2000' and average_temperature.month = month_to_num.month ORDER BY month_to_num.num)
		SELECT month FROM sorted ORDER BY num;
	--For dropdown:--
		SELECT * FROM average_temperature where state = 'Maharashtra';	
		SELECT * FROM average_temperature where state = 'Maharashtra' and year = '2000';
		SELECT * FROM average_temperature where state = 'Maharashtra' and year = '2000' and month = 'August';
	--For dropdown and range:--
		SELECT * FROM average_temperature where state = 'Maharashtra' and year between '2000' and '2001';
	--For the entire avg_temp dataset:--
		SELECT * FROM average_temperature ORDER BY state, year;
	--For corelation between various attributes:--
		--For average temperature and state co2--
			with avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT A.state, A.year, A.avg_temp, B.co2_emissions FROM avg_yearly_temp AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year ORDER BY A.state, A. year;

			with avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT A.state, A.year, A.avg_temp, B.co2_emissions FROM avg_yearly_temp AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' ORDER BY A.state, A. year;
			
			with avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT A.state, A.year, A.avg_temp, B.co2_emissions FROM avg_yearly_temp AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' and A.year = '1985' ORDER BY A.state, A. year;
			
		
		--For average temperature and rainfall--
			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year ORDER BY C.state, D.subdivision, C.year;
			
			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year and C.state = 'Uttar Pradesh' ORDER BY C.state, D.subdivision, C.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year and C.state = 'Uttar Pradesh' and D.subdivision = 'East Uttar Pradesh' ORDER BY C.state, D.subdivision, C.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year and C.state = 'Uttar Pradesh' and D.subdivision = 'East Uttar Pradesh' and C.year = '1985' ORDER BY C.state, D.subdivision, C.year;

--State_CO2--
	--To populate the dropdown:--
		SELECT DISTINCT state FROM state_co2;
		SELECT DISTINCT year FROM state_co2 WHERE state = 'Maharashtra';
	--For dropdown:--
		SELECT * FROM state_co2 where state = 'Maharashtra';
		SELECT * FROM state_co2 where state = 'Maharashtra' and year = '2000';
	--For dropdown and range:--
		SELECT * FROM state_co2 where state = 'Maharashtra' and year between '1999' and '2000';
	--For the entire state_co2 dataset:--	
		SELECT * FROM state_co2 ORDER BY state, year;
	--For corelation between various attributes:--
		--For average temperature and state co2--
			with avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT A.state, A.year, A.avg_temp, B.co2_emissions FROM avg_yearly_temp AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year ORDER BY A.state, A. year;

			with avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT A.state, A.year, A.avg_temp, B.co2_emissions FROM avg_yearly_temp AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' ORDER BY A.state, A. year;
			
			with avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT A.state, A.year, A.avg_temp, B.co2_emissions FROM avg_yearly_temp AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' and A.year = '1985' ORDER BY A.state, A. year;

		--For State_CO2 and rainfall--
			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision)
			SELECT A.state, A.year, A.annual, A.subdivision, B.co2_emissions FROM rainfall_state AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year ORDER BY A.state, A.subdivision, A.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision)
			SELECT A.state, A.year, A.annual, A.subdivision, B.co2_emissions FROM rainfall_state AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' ORDER BY A.state, A.subdivision, A.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision)
			SELECT A.state, A.year, A.annual, A.subdivision, B.co2_emissions FROM rainfall_state AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' and A.subdivision = 'East Uttar Pradesh' ORDER BY A.state, A.subdivision, A.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision)
			SELECT A.state, A.year, A.annual, A.subdivision, B.co2_emissions FROM rainfall_state AS A, state_co2 AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Uttar Pradesh' and A.subdivision = 'East Uttar Pradesh' and A.year = '1985' ORDER BY A.state, A.subdivision, A.year;

--CO2--
	--To populate the dropdown:--
		SELECT DISTINCT year FROM co2;
	--For dropdown:--
		SELECT * FROM co2 where year = '2000';
	--For dropdown and range:--
		SELECT * FROM co2 where year between '2020' and '2021';
	--For the entire co2 dataset:--
		SELECT * FROM co2 ORDER BY year;
	--For different attributes--
		SELECT co2_per_capita, year, gdp FROM co2 ORDER BY year;
		SELECT land_use_change_co2_per_capita, year, gdp FROM co2 ORDER BY year;

--Sealevel--
	--To poulate dropdown options--
		SELECT DISTINCT state FROM sealevel;
		SELECT DISTINCT sea_shore_city FROM sealevel WHERE state = 'Maharashtra';
		SELECT DISTINCT year FROM sealevel WHERE state = 'Maharashtra' and sea_shore_city = 'Bombay';
		with month_to_num(month, num) AS (SELECT month, case when month='January' then 1 else case when month = 'February' then 2 else case when month = 'March' then 3 else case when month = 'April' then 4 else case when month = 'May' then 5 else case when month = 'June' then 6 else case when month = 'July' then 7 else case when month = 'August' then 8 else case when month = 'September' then 9 else case when month = 'October' then 10 else case when month = 'November' then 11 else case when month = 'December' then 12 end end end end end end end end end end end end AS num FROM sealevel ORDER BY num),
		sorted(month) AS (SELECT DISTINCT sealevel.month, num FROM sealevel, month_to_num WHERE state = 'Maharashtra' and sea_shore_city = 'Bombay' and year = '2006' and sealevel.month = month_to_num.month ORDER BY month_to_num.num)
		SELECT month FROM sorted ORDER BY num;
	--For dropdown:--
		SELECT * FROM sealevel where state = 'Maharashtra';
		SELECT * FROM sealevel where state = 'Maharashtra' and sea_shore_city = 'Bombay';
		SELECT * FROM sealevel where state = 'Maharashtra' and sea_shore_city = 'Bombay' and year = '2006';
		SELECT * FROM sealevel where state = 'Maharashtra' and sea_shore_city = 'Bombay' and year = '2006' and month = 'January';
	--For dropdown and range:--
		SELECT * FROM sealevel where state = 'Maharashtra' and sea_shore_city = 'Bombay' and year between '1990' and '2006';
		SELECT * FROM sealevel where state = 'Maharashtra' and sea_shore_city = 'Bombay' and year between '1990' and '2006' and month between 'June' and 'September';
	--For the entire sealevel dataset:--
		SELECT * FROM sealevel ORDER BY state, sea_shore_city, year, month;
		

--AQI--
	--To populate dropdown options--
		SELECT DISTINCT State FROM AQI;
		SELECT DISTINCT City FROM AQI WHERE State='Gujarat';
	--For dropdown--
		SELECT * FROM AQI WHERE State ='Gujarat';
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad';
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad' AND EXTRACT(YEAR FROM DATE)='2015';
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad' AND EXTRACT(YEAR FROM DATE)='2015' AND EXTRACT(MONTH FROM DATE)='01';
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad' AND EXTRACT(YEAR FROM DATE)='2015' AND EXTRACT(MONTH FROM DATE)='01' AND EXTRACT(DAY FROM DATE)='01';
	--For dropdown and range--
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad' AND EXTRACT(YEAR FROM DATE) BETWEEN '2015' AND '2016';
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad' AND EXTRACT(YEAR FROM DATE)='2015' AND EXTRACT(MONTH FROM DATE) BETWEEN '01' AND '03';
		SELECT * FROM AQI WHERE State='Gujarat' AND City='Ahmedabad' AND EXTRACT(YEAR FROM DATE)='2015' AND EXTRACT(MONTH FROM DATE)='01' AND EXTRACT(DAY FROM DATE) BETWEEN '1' AND '15';
	--For the entire AQI dataset--
		SELECT * FROM AQI ORDER BY State,City,Date;
	--For different attributes--
		SELECT city, state, date, pm2_5 FROM AQI ORDER BY state, city, date;
		SELECT city, state, date, pm10 FROM AQI ORDER BY state, city, date;
		SELECT city, state, date, aqi FROM AQI ORDER BY state, city, date;

--Rainfall--
	--To populate the dropdown options--
		SELECT DISTINCT Subdivision FROM Rainfall;
		SELECT DISTINCT Year FROM Rainfall WHERE Subdivision='Sikkim';
	--For dropdown--
		SELECT * FROM Rainfall WHERE Subdivision='Sikkim';
		SELECT * FROM Rainfall WHERE Subdivision='Sikkim' AND Year='1947';
	--For dropdown and range--
		SELECT * FROM Rainfall WHERE Subdivision='Sikkim' AND Year BETWEEN '1947' AND '1970';
	--For the entire rainfall dataset--
		SELECT * FROM Rainfall ORDER BY Subdivision,Year;
	--For different attributes--
		SELECT subdivision, year, annual FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, january_february FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, march_may FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, june_september FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, october_december FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, January FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, February FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, March FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, April FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, May FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, June FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, July FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, August FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, September FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, October FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, November FROM Rainfall ORDER BY subdivision, year;
		SELECT subdivision, year, December FROM Rainfall ORDER BY subdivision, year;
		--For each of these queries we can have ranges? and selections?--
	
	--For correlation between various attributes--
		--For average temperature and rainfall--
			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year ORDER BY C.state, D.subdivision, C.year;
			
			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year and C.state = 'Uttar Pradesh' ORDER BY C.state, D.subdivision, C.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year and C.state = 'Uttar Pradesh' and D.subdivision = 'East Uttar Pradesh' ORDER BY C.state, D.subdivision, C.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			avg_yearly_temp(avg_temp, state, year) AS (SELECT avg(Average_Temperature), state, year FROM average_temperature GROUP BY state, year)
			SELECT C.state, C.avg_temp, C.year, D.subdivision, D.annual FROM avg_yearly_temp AS C, rainfall_state AS D WHERE C.state = D.state and C.year = D.year and C.state = 'Uttar Pradesh' and D.subdivision = 'East Uttar Pradesh' and C.year = '1985' ORDER BY C.state, D.subdivision, C.year;
		
		--For sealevel and rainfall--
			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			rainfall_state_avg(state, annual, year) AS (SELECT state, avg(annual), year FROM rainfall_state GROUP BY state, year),
			avg_yearly_sealevel(state, year, sealevel) AS (SELECT state, year, avg(monthly_msl) FROM sealevel GROUP BY state, year)
			SELECT A.state, A.year, A.annual, B.sealevel FROM rainfall_state_avg AS A, avg_yearly_sealevel AS B WHERE A.state = B.state and A.year = B.year ORDER BY A.state, A.year; 

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			rainfall_state_avg(state, annual, year) AS (SELECT state, avg(annual), year FROM rainfall_state GROUP BY state, year),
			avg_yearly_sealevel(state, year, sealevel) AS (SELECT state, year, avg(monthly_msl) FROM sealevel GROUP BY state, year)
			SELECT A.state, A.year, A.annual, B.sealevel FROM rainfall_state_avg AS A, avg_yearly_sealevel AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Andhra Pradesh' ORDER BY A.state, A.year;

			with rainfall_state(state, subdivision, annual, year) AS (SELECT A.state, B.subdivision, B.annual, B.year FROM state_subdivision AS A, rainfall AS B where B.subdivision = A.subdivision),
			rainfall_state_avg(state, annual, year) AS (SELECT state, avg(annual), year FROM rainfall_state GROUP BY state, year),
			avg_yearly_sealevel(state, year, sealevel) AS (SELECT state, year, avg(monthly_msl) FROM sealevel GROUP BY state, year)
			SELECT A.state, A.year, A.annual, B.sealevel FROM rainfall_state_avg AS A, avg_yearly_sealevel AS B WHERE A.state = B.state and A.year = B.year and A.state = 'Andhra Pradesh' and A.year = '1985' ORDER BY A.state, A.year;
			
