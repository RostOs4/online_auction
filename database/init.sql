-- Создание схемы
CREATE SCHEMA IF NOT EXISTS auction;

-- Выбор схемы как текущую
SET search_path TO auction;

-- Таблица Пользователи
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    phone_number VARCHAR,
    address VARCHAR,
    email VARCHAR NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verification_status VARCHAR NOT NULL,
    is_delited BOOLEAN NOT NULL
);

-- Таблица Баковские карты
CREATE TABLE IF NOT EXISTS Cards (
    card_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    card_number VARCHAR NOT NULL,
    card_period VARCHAR NOT NULL,
    card_cvv VARCHAR NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Таблица История поиска
CREATE TABLE IF NOT EXISTS Search (
    search_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    query TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Таблица Сообщение о проблах
CREATE TABLE IF NOT EXISTS Problems (
    problem_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    problem_text TEXT NOT NULL,
    admin_answer TEXT,
    is_fixed BOOLEAN NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Таблица Категории
CREATE TABLE IF NOT EXISTS Categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    parent_category_id INT,
    FOREIGN KEY (parent_category_id) REFERENCES Categories(category_id) ON DELETE SET NULL
);

-- Таблица Аукционы
CREATE TABLE IF NOT EXISTS Auctions (
    auction_id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    status VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE CASCADE
);

-- Таблица Оценки аукционов
CREATE TABLE IF NOT EXISTS Auctions_Feedback (
    feedback_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    auction_id INT NOT NULL,
    dignities TEXT,
    disadvantages TEXT,
    comment TEXT,
    stars_count INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (auction_id) REFERENCES Auctions(auction_id) ON DELETE CASCADE
);

-- Таблица Фотографии отзывов
CREATE TABLE IF NOT EXISTS Feedback_Photos (
    photo_id SERIAL PRIMARY KEY,
    feedback_id INT NOT NULL,
    url VARCHAR NOT NULL,
    FOREIGN KEY (feedback_id) REFERENCES Auctions_Feedback(feedback_id) ON DELETE CASCADE
);

-- Таблица Видео отзывов
CREATE TABLE IF NOT EXISTS Feedback_Videos (
    video_id SERIAL PRIMARY KEY,
    feedback_id INT NOT NULL,
    url VARCHAR NOT NULL,
    FOREIGN KEY (feedback_id) REFERENCES Auctions_Feedback(feedback_id) ON DELETE CASCADE
);

-- Таблица Просмотры
CREATE TABLE IF NOT EXISTS Viewing (
    viewing_id SERIAL PRIMARY KEY,
    auction_id INT NOT NULL,
    user_id INT NOT NULL,
    time TIMESTAMP NOT NULL,
    FOREIGN KEY (auction_id) REFERENCES Auctions(auction_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Таблица Заявки на участие
CREATE TABLE IF NOT EXISTS Introduction (
    introduction_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    auction_id INT NOT NULL,
    status VARCHAR NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (auction_id) REFERENCES Auctions(auction_id) ON DELETE CASCADE
);

-- Таблица Лоты
CREATE TABLE IF NOT EXISTS Items (
    item_id SERIAL PRIMARY KEY,
    auction_id INT NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    initial_bid DECIMAL,
    min_difference_bid DECIMAL,
    status VARCHAR NOT NULL,
    FOREIGN KEY (auction_id) REFERENCES Auctions(auction_id) ON DELETE CASCADE
);

-- Таблица Фотографии лота
CREATE TABLE IF NOT EXISTS Item_Photos (
    photo_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    url VARCHAR NOT NULL,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE
);

-- Таблица Видео лота
CREATE TABLE IF NOT EXISTS Item_Videos (
    video_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    url VARCHAR NOT NULL,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE
);

-- Таблица Сообщения
CREATE TABLE IF NOT EXISTS Messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INT NOT NULL,
    recipient_id INT NOT NULL,
    item_id INT,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (sender_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE SET NULL
);

-- Таблица Ставки
CREATE TABLE IF NOT EXISTS Bids (
    bid_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    bidder_id INT NOT NULL,
    bid_amount DECIMAL NOT NULL,
    bid_time TIMESTAMP NOT NULL,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (bidder_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Таблица Службы доставки
CREATE TABLE IF NOT EXISTS Delivery_Service (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR NOT NULL,
    service_information TEXT NOT NULL,
    contact_name VARCHAR NOT NULL,
    contact_phone VARCHAR,
    contact_mail VARCHAR NOT NULL
);

-- Таблица Доставка
CREATE TABLE IF NOT EXISTS Delivery (
    delivery_id SERIAL PRIMARY KEY,
    lot_id INT NOT NULL,
    service_id INT NOT NULL,
    delivery_cost DECIMAL NOT NULL,
    delivery_time TIMESTAMP NOT NULL,
    delivery_address VARCHAR NOT NULL,
    delivery_status VARCHAR NOT NULL,
    delivery_date TIMESTAMP,
    FOREIGN KEY (lot_id) REFERENCES Items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES Delivery_Service(service_id) ON DELETE CASCADE
);

-- Таблица Транзакции
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL,
    buyer_id INT NOT NULL,
    bid_id INT NOT NULL,
    delivery_id INT NOT NULL,
    transaction_amount DECIMAL NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    transaction_status VARCHAR NOT NULL,
    buyer_card_id INT NOT NULL,
    seller_card_id INT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (bid_id) REFERENCES Bids(bid_id) ON DELETE CASCADE,
    FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_card_id) REFERENCES Cards(card_id) ON DELETE CASCADE,
    FOREIGN KEY (seller_card_id) REFERENCES Cards(card_id) ON DELETE CASCADE
);

-- Таблица Логи
CREATE TABLE IF NOT EXISTS Logs (
    log_id SERIAL PRIMARY KEY,
    action VARCHAR NOT NULL,
    user_id INT,
    card_id INT,
    search_id INT,
    problem_id INT,
    category_id INT,
    auction_id INT,
    feedback_id INT,
    feedback_photo_id INT,
    feedback_video_id INT,
    viewing_id INT,
    introduction_id INT,
    item_id INT,
    item_photo_id INT,
    item_video_id INT,
    message_id INT,
    bid_id INT,
    service_id INT,
    delivery_id INT,
    transaction_id INT,
    result TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES Cards(card_id) ON DELETE SET NULL,
    FOREIGN KEY (search_id) REFERENCES Search(search_id) ON DELETE SET NULL,
    FOREIGN KEY (problem_id) REFERENCES Problems(problem_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (auction_id) REFERENCES Auctions(auction_id) ON DELETE SET NULL,
    FOREIGN KEY (feedback_id) REFERENCES Auctions_Feedback(feedback_id) ON DELETE SET NULL,
    FOREIGN KEY (feedback_photo_id) REFERENCES Feedback_Photos(photo_id) ON DELETE SET NULL,
    FOREIGN KEY (feedback_video_id) REFERENCES Feedback_Videos(video_id) ON DELETE SET NULL,
    FOREIGN KEY (viewing_id) REFERENCES Viewing(viewing_id) ON DELETE SET NULL,
    FOREIGN KEY (introduction_id) REFERENCES Introduction(introduction_id) ON DELETE SET NULL,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE SET NULL,
    FOREIGN KEY (item_photo_id) REFERENCES Item_Photos(photo_id) ON DELETE SET NULL,
    FOREIGN KEY (item_video_id) REFERENCES Item_Videos(video_id) ON DELETE SET NULL,
    FOREIGN KEY (message_id) REFERENCES Messages(message_id) ON DELETE SET NULL,
    FOREIGN KEY (bid_id) REFERENCES Bids(bid_id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES Delivery_Service(service_id) ON DELETE SET NULL,
    FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id) ON DELETE SET NULL,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id) ON DELETE SET NULL
);