use profile;
CREATE TABLE users (
    child_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    child_name VARCHAR(100) NOT NULL,
    child_age INT NOT NULL
);

CREATE TABLE game_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- Primary key for the game_scores table
    score INT NOT NULL,                          -- Score achieved in the game
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp of when the score was recorded
);

CREATE TABLE children (
    child_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES users(user_id)
);

CREATE TABLE survey_responses (
    survey_id INT AUTO_INCREMENT PRIMARY KEY,
    children_id INT NOT NULL,
    question_number INT NOT NULL,
    response ENUM('yes', 'no') NOT NULL,
    FOREIGN KEY (children_id) REFERENCES children(child_id) ON DELETE CASCADE
);
select *from users;
select * from children;
select *from capturedimages;
select *from game_scores;
select *from survey_responses;





