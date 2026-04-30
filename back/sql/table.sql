CREATE TABLE pred_models (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    model JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE airport_info(
    airport_code CHAR(3) PRIMARY KEY, 
    airport_name_en VARCHAR(128), 
    airport_name_ko VARCHAR(128), 
    taxiout_mean FLOAT, 
    taxiin_mean FLOAT
);

CREATE TABLE airtime (
    route CHAR(7) NOT NULL,
    crs_dep_hour INT NOT NULL,
    airtime_mean FLOAT,

    PRIMARY KEY (route, crs_dep_hour)
);

CREATE TABLE taxi_inout (
    airport_code CHAR(3) NOT NULL,
    operation_hour INT NOT NULL,
    taxiin_mean FLOAT,
    taxiout_mean FLOAT,

    PRIMARY KEY (airport_code, operation_hour)
);