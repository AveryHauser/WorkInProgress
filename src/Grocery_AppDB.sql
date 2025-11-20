CREATE DATABASE IF NOT EXISTS grocery_app;
USE grocery_app;


-- 1. Users
CREATE TABLE user (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    created_at VARCHAR(10) NOT NULL,
    stat VARCHAR(20) NOT NULL
);

-- 2. Users Profile
CREATE TABLE usesr_profile (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY,
    display_name,
    home_store,
    privacy_flags, 
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Session
CREATE TABLE session (
    session_id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    created_at,
    expires_at,
    device_info,
    ip_hash,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE

);

-- 4. Food
CREATE TABLE food (
    product_id VARCHAR(36) NOT NULL PRIMARY KEY,
    name,
    group,
    type,
    av_price,
    cur_demand,
    cur_supply,
);

-- 5. Nutrition
CREATE TABLE nutrition (
    nutrition_id VARCHAR(36) NOT NULL PRIMARY KEY,
    health_scale,
    calories,
    protein,
    fat,
    sugars,
    carb,
    alcohol,
    water,
    caffeine,
    FOREIGN KEY (nutrition_id) REFERENCES food(product_id) ON DELETE CASCADE
);

-- 6. Mineral
CREATE TABLE mineral (
    mineral_id VARCHAR(36) NOT NULL PRIMARY KEY,
    nutrition_id VARCHAR(36) NOT NULL,
    name,
    amount,
    FOREIGN KEY (nutrition_id) REFERENCES nutrition(nutrition_id) ON DELETE CASCADE

);

-- 7. Vitamin
CREATE TABLE vitamin (
    vitamin_id VARCHAR(36) NOT NULL PRIMARY KEY,
    nutrition_id VARCHAR(36) NOT NULL,
    name,
    amount,
    FOREIGN KEY (nutrition_id) REFERENCES nutrition(nutrition_id) ON DELETE CASCADE
);

-- 8. Grocery location
CREATE TABLE grocery_location (
    location_id VARCHAR(36) NOT NULL PRIMARY KEY,
    name,
    address,
);

-- 9. Grocery List
CREATE TABLE grocery_list (
    grocery_id VARCHAR(36) NOT NULL PRIMARY KEY,
    product_id,
    FOREIGN KEY (product_id) REFERENCES food(product_id) ON DELETE CASCADE,
);

-- 10. Budget
CREATE TABLE budget (
    budget_id VARCHAR(36) NOT NULL PRIMARY KEY,
    group,
    price,

 FOREIGN KEY (group) REFERENCES food(group) ON DELETE CASCADE,
);
