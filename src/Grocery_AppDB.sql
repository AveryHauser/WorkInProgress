CREATE DATABASE IF NOT EXISTS grocery_app;
USE grocery_app;

-- 1. Users
CREATE TABLE user (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL,
    stat VARCHAR(20) NOT NULL
);

-- 2. User Profile
CREATE TABLE user_profile (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY,
    display_name VARCHAR(100),
    home_store VARCHAR(100),
    privacy_flags BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 3. Session
CREATE TABLE session (
    session_id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    created_at DATETIME,
    expires_at DATETIME,
    device_info VARCHAR(255),
    ip_hash VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 4. Food
CREATE TABLE food (
    Food_Item_ID VARCHAR(36) NOT NULL PRIMARY KEY, 
    foodname VARCHAR(255) NOT NULL,               
    Category_Name VARCHAR(100),                  
    type VARCHAR(100),
    Cost_per_unit DECIMAL(10,2),                
    cur_demand INT,
    cur_supply INT
);

-- 5. Nutrition
CREATE TABLE nutrition (
    Food_Item_ID VARCHAR(36) NOT NULL PRIMARY KEY, 
    health_scale VARCHAR(50),
    Energy_kcal DECIMAL(10,2),    
    Protein_g DECIMAL(10,2),      
    Total_Fat_g DECIMAL(10,2),    
    Sugars_g DECIMAL(10,2),       
    Carbohydrate_g DECIMAL(10,2), 
    Alcohol_g DECIMAL(10,2),      
    Water_g DECIMAL(10,2),        
    Caffeine_mg DECIMAL(10,2),    
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 6. Mineral
CREATE TABLE mineral (
    mineral_id VARCHAR(36) NOT NULL PRIMARY KEY,
    Food_Item_ID VARCHAR(36) NOT NULL, 
    name VARCHAR(100),
    amount DECIMAL(10,2),
    FOREIGN KEY (Food_Item_ID) REFERENCES nutrition(Food_Item_ID) ON DELETE CASCADE
);

-- 7. Vitamin
CREATE TABLE vitamin (
    vitamin_id VARCHAR(36) NOT NULL PRIMARY KEY,
    Food_Item_ID VARCHAR(36) NOT NULL, 
    name VARCHAR(100),
    amount DECIMAL(10,2),
    FOREIGN KEY (Food_Item_ID) REFERENCES nutrition(Food_Item_ID) ON DELETE CASCADE
);

-- 8. Grocery location
CREATE TABLE grocery_location (
    OBJECTID VARCHAR(36) NOT NULL PRIMARY KEY, 
    STORENAME VARCHAR(255),                    
    STORE_ADDRESS VARCHAR(255)
);

-- 9. Grocery List
CREATE TABLE grocery_list (
    grocery_id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    Food_Item_ID VARCHAR(36) NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 10. Budget
CREATE TABLE budget (
    budget_id VARCHAR(36) NOT NULL PRIMARY KEY,
    budget_group VARCHAR(100),
    price DECIMAL(10,2)
);