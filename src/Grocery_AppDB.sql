CREATE DATABASE IF NOT EXISTS grocery_app;
USE grocery_app;

-- Deleting tables to reset each time the program is run
SET foreign_key_checks = 0;

DROP TABLE IF EXISTS user_profile;
DROP TABLE IF EXISTS session;
DROP TABLE IF EXISTS nutrition;
DROP TABLE IF EXISTS mineral;
DROP TABLE IF EXISTS vitamin;
DROP TABLE IF EXISTS food_dietary_map;
DROP TABLE IF EXISTS dietary_tag;
DROP TABLE IF EXISTS store_product;
DROP TABLE IF EXISTS grocery_location;
DROP TABLE IF EXISTS market_price;
DROP TABLE IF EXISTS pantry;
DROP TABLE IF EXISTS recipe;
DROP TABLE IF EXISTS recipe_ingredient;
DROP TABLE IF EXISTS user_review;
DROP TABLE IF EXISTS county_health_data;
DROP TABLE IF EXISTS grocery_list_item;
DROP TABLE IF EXISTS grocery_list;
DROP TABLE IF EXISTS food;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS user;

SET foreign_key_checks = 1;

-- 1. Users
CREATE TABLE user (
    user_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    stat VARCHAR(20) NOT NULL
);

-- 2. User Profile
CREATE TABLE user_profile (
    user_id INT NOT NULL,
    display_name VARCHAR(100),
    home_store VARCHAR(100),
    privacy_flags BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 3. Session
CREATE TABLE session (
    session_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    device_info VARCHAR(255),
    ip_hash VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 4. Category (Matches 'Food_Categories.csv')
CREATE TABLE category (
    Category_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    Category_Name VARCHAR(100),
    Active BOOLEAN DEFAULT 1
);

-- 5. Food (Updated to link to Category_ID)
CREATE TABLE food (
    Food_Item_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
    foodname VARCHAR(255) NOT NULL,               
    Category_ID INT, 
    type VARCHAR(100),
    Cost_per_unit DECIMAL(10,2),                
    cur_demand INT DEFAULT 0,
    cur_supply INT DEFAULT 0,
    FOREIGN KEY (Category_ID) REFERENCES category(Category_ID)
);

-- 6. Nutrition (Macro nutrients from 'Nutrients.csv')
CREATE TABLE nutrition (
    Food_Item_ID INT NOT NULL, 
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

-- 7. Mineral (Micro nutrients from 'Nutrients.csv')
CREATE TABLE mineral (
    mineral_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    Food_Item_ID INT NOT NULL, 
    name VARCHAR(100), -- e.g., 'Calcium', 'Iron'
    amount DECIMAL(10,2),
    unit VARCHAR(20), -- e.g., 'mg', 'mcg'
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 8. Vitamin (Micro nutrients from 'Nutrients.csv')
CREATE TABLE vitamin (
    vitamin_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    Food_Item_ID INT NOT NULL, 
    name VARCHAR(100), -- e.g., 'Vitamin C', 'Vitamin A'
    amount DECIMAL(10,2),
    unit VARCHAR(20),
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 9. Dietary Tag (e.g., Gluten-Free, Vegan)
CREATE TABLE dietary_tag (
    tag_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    tag_name VARCHAR(50) UNIQUE
);

-- 10. Food Dietary Map (Links Food to Tags)
CREATE TABLE food_dietary_map (
    map_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    Food_Item_ID INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES dietary_tag(tag_id) ON DELETE CASCADE
);

-- 11. Grocery Location (Matches 'Grocery_Store_Locations.csv')
CREATE TABLE grocery_location (
    OBJECTID INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
    STORENAME VARCHAR(255),         
    STORE_ADDRESS VARCHAR(255),
    zipcode VARCHAR(10),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

-- 12. Market Price (Matches 'Vegetable-Prices-2022.csv' & PPI Data)
-- Tracks general market prices (not specific to one store)
CREATE TABLE market_price (
    price_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    Food_Item_ID INT,
    price_per_unit DECIMAL(10,2),
    unit_type VARCHAR(50), -- e.g., 'per pound'
    data_year INT, -- e.g., 2022
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE SET NULL
);

-- 13. Store Product (Links Food to a specific Grocery Location)
CREATE TABLE store_product (
    store_product_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    OBJECTID INT NOT NULL, 
    Food_Item_ID INT NOT NULL,
    local_price DECIMAL(10,2),
    in_stock BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (OBJECTID) REFERENCES grocery_location(OBJECTID) ON DELETE CASCADE,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 14. Grocery List (Header Table)
CREATE TABLE grocery_list (
    grocery_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    list_name VARCHAR(100) DEFAULT 'My List',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 15. Grocery List Item (The actual items)
CREATE TABLE grocery_list_item (
    list_item_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    grocery_id INT NOT NULL,
    Food_Item_ID INT NOT NULL,
    quantity INT DEFAULT 1,
    is_checked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (grocery_id) REFERENCES grocery_list(grocery_id) ON DELETE CASCADE,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 16. Pantry (User Inventory)
CREATE TABLE pantry (
    pantry_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    Food_Item_ID INT NOT NULL,
    quantity_on_hand DECIMAL(10,2),
    expiry_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 17. Recipe
CREATE TABLE recipe (
    recipe_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    prep_time_minutes INT,
    cook_time_minutes INT,
    servings INT,
    instructions TEXT
);

-- 18. Recipe Ingredient
CREATE TABLE recipe_ingredient (
    recipe_ingredient_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    recipe_id INT NOT NULL,
    Food_Item_ID INT NOT NULL,
    amount DECIMAL(10,2),
    unit VARCHAR(50),
    FOREIGN KEY (recipe_id) REFERENCES recipe(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 19. User Review
CREATE TABLE user_review (
    review_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    Food_Item_ID INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (Food_Item_ID) REFERENCES food(Food_Item_ID) ON DELETE CASCADE
);

-- 20. County Health Data (Matches 'StateAndCountyData.csv')
CREATE TABLE county_health_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    FIPS VARCHAR(10),
    State VARCHAR(50),
    County VARCHAR(100),
    Variable_Code VARCHAR(50), 
    Value DECIMAL(15, 4)      
);