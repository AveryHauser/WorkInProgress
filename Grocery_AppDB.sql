CREATE DATABASE IF NOT EXISTS grocery_app;
USE grocery_app;


-- 1. Users
CREATE TABLE users (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY
    email VARCHAR(50) UNIQUE NOT NULL
    password_hash VARCHAR(100) NOT NULL

);

-- 2. Users Profile
CREATE TABLE usesrs_profile (

);

-- 3. Session
CREATE TABLE session (

);

-- 4. Food
CREATE TABLE food (

);

-- 5. Nutrition
CREATE TABLE nutrition (

);

-- 6. Mineral
CREATE TABLE mineral (
    mineral_id VARCHAR(30) NOT NULL PRIMARY KEY
    
);

-- 7. Vitamin
CREATE TABLE vitamin (
    
);

-- 8. Grocery location
CREATE TABLE grocery_location (

);

-- 9. Grocery List
CREATE TABLE grocery_list (

);

-- 10. Budget
CREATE TABLE budget (

);
