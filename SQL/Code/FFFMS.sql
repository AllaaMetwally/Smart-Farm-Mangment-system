
CREATE SCHEMA smartfarm;
SET search_path = smartfarm;

CREATE TABLE Plants (
    Plant_ID integer PRIMARY KEY ,
    Name character varying(100) NOT NULL,
    Type character varying(50),
    Area numeric(10,2),
    Water_Need numeric(5,2),
    Fertilizer character varying(100),
    Plant_Date date,
    Harvest_Date date
);

CREATE TABLE Animals (
   Animal_ID  int PRIMARY KEY,
   Type  VARCHAR (25),
   Age int,
   Weight int,
   Health_Status  VARCHAR (25),
   Vaccination_Date  VARCHAR (25)
   
);


CREATE TABLE Workers (
    Worker_ID   integer  PRIMARY KEY ,
    Name   VARCHAR(50) NOT NULL,
    Job VARCHAR(50),
    Phone numeric ,
    Salary numeric(10,2),
    Shift VARCHAR(50)
);

CREATE TABLE Equipments(
    Equipment_ID INT PRIMARY KEY,
	Name VARCHAR (25),
	Condition VARCHAR (25),
	Purchase_Date VARCHAR (25),
	Maintenance_Date VARCHAR (25)
);

ALTER TABLE Equipments
ALTER COLUMN Purchase_Date TYPE DATE USING Purchase_Date::DATE,
ALTER COLUMN Maintenance_Date TYPE DATE USING Maintenance_Date::DATE;

CREATE TABLE Sales (
    Sale_ID INT PRIMARY KEY,
    Product_Type VARCHAR(10) CHECK (product_type IN ('plant', 'animal')),
	Product_ID  INT NOT NULL, 
    Quantity INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    Date DATE NOT NULL
);

CREATE TABLE Plant_Sales (
    Sale_ID INT PRIMARY KEY,
    Plant_ID INT NOT NULL,
    CONSTRAINT fk_plant_sale FOREIGN KEY (Sale_ID) REFERENCES Sales(Sale_ID) ON DELETE CASCADE,
    CONSTRAINT fk_plant_id FOREIGN KEY (Plant_ID) REFERENCES Plants(Plant_ID)
);

CREATE TABLE Animal_Sales (
    Sale_ID INT PRIMARY KEY,
    Animal_ID INT NOT NULL,
    CONSTRAINT fk_animal_sale FOREIGN KEY (Sale_ID) REFERENCES Sales(Sale_ID) ON DELETE CASCADE,
    CONSTRAINT fk_animal_id FOREIGN KEY (Animal_ID) REFERENCES Animals(Animal_ID)
);


CREATE TABLE Expenses(
    Expense_ID INT PRIMARY KEY,
	Type VARCHAR (25),
	Amount NUMERIC ,  
	Date DATE 	
);

CREATE TABLE Crops_Growth (
    Growth_ID integer  PRIMARY KEY ,
    Plant_ID integer NOT NULL,
    Stage_Name character varying(100),
    Date date ,
    Notes text,
	CONSTRAINT crop_plant FOREIGN KEY (Plant_ID) REFERENCES Plants(Plant_ID) 

);

CREATE TABLE Animal_Health_Log (
     HealthLog_ID int PRIMARY KEY ,
	 Animal_ID INT,
	 Check_Date DATE ,
	 Symptoms VARCHAR (25),
	 Treatment VARCHAR (25),
	 CONSTRAINT Health_ani_fk FOREIGN KEY (Animal_ID) REFERENCES Animals (Animal_ID)

);

CREATE TABLE Maintenance_Log (
    Log_ID integer  PRIMARY KEY ,
	Equipment_ID int ,
    Maintenance_Date date,
    Description text,
    Worker_ID integer,
	CONSTRAINT main_eqi_fk FOREIGN KEY (Equipment_ID) REFERENCES Equipments(Equipment_ID)

);

ALTER TABLE Maintenance_Log
ADD CONSTRAINT main_worker_fk
FOREIGN KEY (Worker_ID) REFERENCES Workers(Worker_ID);

CREATE TABLE Worker_Assignments (
   Assignment_ID INT PRIMARY KEY,
   Worker_ID int ,
   Plant_ID int ,
   Animal_ID int,
   Task VARCHAR (25),
   Date date ,
   CONSTRAINT ass_wor_fk FOREIGN KEY (Worker_ID) REFERENCES Workers(Worker_ID),
   CONSTRAINT ass_pla_fk FOREIGN KEY (Plant_ID) REFERENCES Plants(Plant_ID),  
   CONSTRAINT ass_ani_fk FOREIGN KEY (Animal_ID) REFERENCES Animals(Animal_ID)
   
);

COPY smartfarm.Plants
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Plants.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Plants ;


COPY smartfarm.animals
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Animals.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Animals ;



COPY smartfarm.Workers
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Workers.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Workers ;

COPY smartfarm.Equipments
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Equipments.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Equipments ;

COPY smartfarm.Sales
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Sales.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Sales ;

COPY smartfarm.Expenses
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Expenses.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Expenses ;

COPY smartfarm.Crops_Growth
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Crops_Growth.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Crops_Growth ;

COPY smartfarm.Animal_Health_Log
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Animal_Health_Log.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Animal_Health_Log ;

COPY smartfarm.Maintenance_Log
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Maintenance_Log.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Maintenance_Log ;

COPY smartfarm.Worker_Assignments
FROM 'C:/Users/hp/OneDrive/Desktop/Lectures/Database/csv/Worker_Assignments.csv'
DELIMITER ',' CSV HEADER;

SELECT * from Worker_Assignments ;

INSERT INTO Plant_Sales (Sale_ID, Plant_ID)
SELECT Sale_ID, Product_ID
FROM Sales
WHERE Product_Type = 'plant';

INSERT INTO Animal_Sales (Sale_ID, Animal_ID)
SELECT Sale_ID, Product_ID
FROM Sales
WHERE Product_Type = 'animal';

-- Create roles
CREATE ROLE farm_owner LOGIN PASSWORD 'owner123';
CREATE ROLE farm_worker LOGIN PASSWORD 'worker123';
CREATE ROLE farm_visitor LOGIN PASSWORD 'visitor123';

-- Give schema access
GRANT USAGE ON SCHEMA smartfarm TO farm_owner, farm_worker, farm_visitor;

-- Owner: full access
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA smartfarm TO farm_owner;

-- Worker: read tasks + confirm
GRANT SELECT, UPDATE ON smartfarm.Worker_Assignments TO farm_worker;
GRANT SELECT ON smartfarm.Crops_Growth TO farm_worker;
GRANT SELECT ON smartfarm.Animal_Health_Log TO farm_worker;

-- Visitor: read prices only
GRANT SELECT ON smartfarm.Sales TO farm_visitor;
GRANT SELECT ON smartfarm.Plant_Sales TO farm_visitor;
GRANT SELECT ON smartfarm.Animal_Sales TO farm_visitor;


-- Plants table
ALTER TABLE smartfarm.Plants
ALTER COLUMN Plant_ID ADD GENERATED BY DEFAULT AS IDENTITY;
-- Animals table
ALTER TABLE smartfarm.Animals
ALTER COLUMN Animal_ID ADD GENERATED BY DEFAULT AS IDENTITY;

-- Workers table
ALTER TABLE smartfarm.Workers
ALTER COLUMN Worker_ID ADD GENERATED BY DEFAULT AS IDENTITY;

-- Equipments table
ALTER TABLE smartfarm.Equipments
ALTER COLUMN Equipment_ID ADD GENERATED BY DEFAULT AS IDENTITY;

-- Sales table
ALTER TABLE smartfarm.Sales
ALTER COLUMN Sale_ID ADD GENERATED BY DEFAULT AS IDENTITY;

-- Expenses table
ALTER TABLE smartfarm.Expenses
ALTER COLUMN Expense_ID ADD GENERATED BY DEFAULT AS IDENTITY;

-- Allow viewer to see tables
GRANT SELECT ON
    plants,
    animals,
    crops_growth,
    workers,
    equipments,
    sales,
    expenses,
    animal_health_log,
    maintenance_log,
    worker_assignments
TO farm_visitor;

GRANT SELECT, INSERT, UPDATE ON
    plants,
    crops_growth,
    worker_assignments
TO farm_worker;

GRANT SELECT ON
    animals,
    equipments,
    workers
TO farm_worker;
