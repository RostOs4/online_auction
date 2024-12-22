# Инициализация приложения
from flask import Flask, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from forms import LoginForm, RegistrationForm, EditAccountForm
from werkzeug.utils import secure_filename
import re
import datetime
import time
import os
import jwt

app = Flask(__name__)

app.config['SECRET_KEY'] = "a37ahdea3238fhew328fedr43843gfergq34"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://auction:auction@localhost:1000/auction'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://auction:auction@postgres:5432/auction'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']

UPLOAD_FOLDER = 'upload_files/'  # Укажите путь к папке для загрузки
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}  # Разрешенные расширения
SECRET_KEY = 'your_secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    phone_number = db.Column(db.String)
    address = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    registration_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    cards = db.relationship('Card', back_populates='user')
    searches = db.relationship('Search', back_populates='user')
    problems = db.relationship('Problem', back_populates='user')

class Card(db.Model):
    __tablename__ = 'cards'
    
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    card_number = db.Column(db.String, nullable=False)
    card_period = db.Column(db.String, nullable=False)
    card_cvv = db.Column(db.String, nullable=False)

    user = db.relationship('User', back_populates='cards')

class Search(db.Model):
    __tablename__ = 'searches'
    
    search_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    query = db.Column(db.String, nullable=False)

    user = db.relationship('User', back_populates='searches')

class Problem(db.Model):
    __tablename__ = 'problems'
    
    problem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    problem_text = db.Column(db.String, nullable=False)
    admin_answer = db.Column(db.String)
    is_fixed = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', back_populates='problems')

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)

    parent_category = db.relationship('Category', remote_side=[category_id], backref='subcategories')

class Auction(db.Model):
    __tablename__ = 'auctions'
    
    auction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    status = db.Column(db.String, nullable=False, default='active')
    auction_type = db.Column(db.String, nullable=False)

    seller = db.relationship('User', backref='auctions')
    category = db.relationship('Category', backref='auctions')

class AuctionFeedback(db.Model):
    __tablename__ = 'auctions_feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.auction_id'), nullable=False)
    dignities = db.Column(db.String)
    disadvantages = db.Column(db.String)
    comment = db.Column(db.String)
    stars_count = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='feedbacks')
    auction = db.relationship('Auction', backref='feedbacks')

class FeedbackPhoto(db.Model):
    __tablename__ = 'feedback_photos'
    
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('auctions_feedback.feedback_id'), nullable=False)
    url = db.Column(db.String, nullable=False)

    feedback = db.relationship('AuctionFeedback', backref='photos')

class FeedbackVideo(db.Model):
    __tablename__ = 'feedback_videos'
    
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('auctions_feedback.feedback_id'), nullable=False)
    url = db.Column(db.String, nullable=False)

    feedback = db.relationship('AuctionFeedback', backref='videos')

class Viewing(db.Model):
    __tablename__ = 'viewings'
    
    viewing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.auction_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    auction = db.relationship('Auction', backref='viewings')
    user = db.relationship('User', backref='viewings')

class Introduction(db.Model):
    __tablename__ = 'introductions'
    
    introduction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.auction_id'), nullable=False)
    status = db.Column(db.String, nullable=False)

    user = db.relationship('User', backref='introductions')
    auction = db.relationship('Auction', backref='introductions')

class Item(db.Model):
    __tablename__ = 'items'
    
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.auction_id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    initial_bid = db.Column(db.Float) 
    min_difference_bid = db.Column(db.Float)
    status = db.Column(db.String, nullable=False)

    auction = db.relationship('Auction', backref='items')

class ItemPhoto(db.Model):
    __tablename__ = 'item_photos'
    
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    url = db.Column(db.String, nullable=False)

    item = db.relationship('Item', backref='photos')

class ItemVideo(db.Model):
    __tablename__ = 'item_videos'
    
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    url = db.Column(db.String, nullable=False)

    item = db.relationship('Item', backref='videos')

class Message(db.Model):
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=True)
    message = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    item = db.relationship('Item', backref='messages')

class Bid(db.Model):
    __tablename__ = 'bids'
    
    bid_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
    bid_time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    item = db.relationship('Item', backref='bids')
    bidder = db.relationship('User', backref='bids')

class DeliveryService(db.Model):
    __tablename__ = 'delivery_services'
    
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String, nullable=False)
    service_information = db.Column(db.String, nullable=False)
    contact_name = db.Column(db.String, nullable=False)
    contact_phone = db.Column(db.String)
    contact_mail = db.Column(db.String, nullable=False)

class Deliveries(db.Model):
    __tablename__ = 'deliveries'
    
    delivery_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('delivery_services.service_id'), nullable=False)
    delivery_cost = db.Column(db.Float, nullable=False)
    delivery_time = db.Column(db.String, nullable=False)  # Можно использовать более точный тип данных, если необходимо
    delivery_address = db.Column(db.String, nullable=False)
    delivery_status = db.Column(db.String, nullable=False)
    delivery_date = db.Column(db.DateTime)

    lot = db.relationship('Item', backref='deliveries')
    service = db.relationship('DeliveryService', backref='deliveries')

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    bid_id = db.Column(db.Integer, db.ForeignKey('bids.bid_id'), nullable=False)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.delivery_id'), nullable=False)
    transaction_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    transaction_status = db.Column(db.String, nullable=False)
    buyer_card_id = db.Column(db.Integer, db.ForeignKey('cards.card_id'), nullable=False)
    seller_card_id = db.Column(db.Integer, db.ForeignKey('cards.card_id'), nullable=False)  # Исправлено на seller_card_id

    seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
    bid = db.relationship('Bid', backref='transactions')
    delivery = db.relationship('Deliveries', backref='transactions')

class Log(db.Model):
    __tablename__ = 'logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.card_id'), nullable=True)
    search_id = db.Column(db.Integer, db.ForeignKey('searches.search_id'), nullable=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.problem_id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.auction_id'), nullable=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('auctions_feedback.feedback_id'), nullable=True)
    feedback_photo_id = db.Column(db.Integer, db.ForeignKey('feedback_photos.photo_id'), nullable=True)
    feedback_video_id = db.Column(db.Integer, db.ForeignKey('feedback_videos.video_id'), nullable=True)
    viewing_id = db.Column(db.Integer, db.ForeignKey('viewings.viewing_id'), nullable=True)
    introduction_id = db.Column(db.Integer, db.ForeignKey('introductions.introduction_id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=True)
    item_photo_id = db.Column(db.Integer, db.ForeignKey('item_photos.photo_id'), nullable=True)
    item_video_id = db.Column(db.Integer, db.ForeignKey('item_videos.video_id'), nullable=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bids.bid_id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('delivery_services.service_id'), nullable=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.delivery_id'), nullable=True)

with app.app_context():
    db.create_all()

def log_action(action, user_id=None, card_id=None, search_id=None, problem_id=None,
               category_id=None, auction_id=None, feedback_id=None, feedback_photo_id=None,
               feedback_video_id=None, viewing_id=None, introduction_id=None, item_id=None,
               item_photo_id=None, item_video_id=None, message_id=None, bid_id=None,
               service_id=None, delivery_id=None):
    # Создаем новый объект Log
    new_log = Log(
        action=action,
        user_id=user_id,
        card_id=card_id,
        search_id=search_id,
        problem_id=problem_id,
        category_id=category_id,
        auction_id=auction_id,
        feedback_id=feedback_id,
        feedback_photo_id=feedback_photo_id,
        feedback_video_id=feedback_video_id,
        viewing_id=viewing_id,
        introduction_id=introduction_id,
        item_id=item_id,
        item_photo_id=item_photo_id,
        item_video_id=item_video_id,
        message_id=message_id,
        bid_id=bid_id,
        service_id=service_id,
        delivery_id=delivery_id
    )
    db.session.add(new_log)
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Проверка, вошел ли пользователь в систему
    token = request.cookies.get('token')  # Проверяем наличие токена в куках
    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return redirect(url_for('account'))  # Перенаправление на главную страницу
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            # Удаляем истекший токен
            response = make_response(redirect(url_for('login')))
            response.set_cookie('token', '', expires=0)  # Удаляем токен
            return response
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            # Удаляем недействительный токен
            response = make_response(redirect(url_for('login')))
            response.set_cookie('token', '', expires=0)  # Удаляем токен
            return response

    form = LoginForm()  # Создайте экземпляр формы
    if form.validate_on_submit():  # Проверка, отправлена ли форма и валидна ли она
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Генерация JWT токена
            token = jwt.encode({
                'user_id': user.user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Токен будет действителен 1 час
            }, SECRET_KEY, algorithm='HS256')

            # Устанавливаем токен в куки
            response = make_response(redirect(url_for('index')))  # Перенаправление на главную страницу
            response.set_cookie('token', token, httponly=True)  # Устанавливаем токен в куки
            flash('Вы успешно вошли!', 'success')
            
            # Логируем успешный вход
            log_action(action='login_success', user_id=user.user_id)
            return response
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect(url_for('login')))  # Перенаправляем на страницу входа
    response.set_cookie('token', '', expires=0)  # Удаляем токен из куков
    flash('Вы вышли из системы.', 'success')
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  
    if form.validate_on_submit():  
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data  # Получаем значение из поля подтверждения пароля

        # Проверка существования пользователя с такой почтой
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Пользователь с таким email уже существует!', 'danger')
            return render_template('register.html', form=form)
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем пользователя уже существует!', 'danger')
            return render_template('register.html', form=form)

        # Проверка качества пароля (простейшая проверка)
        if len(password) < 8 or not re.search("[A-Z]", password) or not re.search("[a-z]", password) or not re.search("[0-9]", password):
            flash('Пароль должен содержать минимум 8 символов, заглавные и строчные буквы латинского алфавита, а также цифры.', 'danger')
            return render_template('register.html', form=form)

        # Проверка совпадения пароля и подтверждения пароля
        if password != confirm_password:
            flash('Пароли не совпадают!', 'danger')
            return render_template('register.html', form=form)

        new_user = User(username=username, email=email, password=password)  
        db.session.add(new_user)  
        db.session.commit()  
        flash('Вы успешно зарегистрировались!', 'success')
        log_action(action="registration_success", user_id=new_user.user_id)

        # Генерация JWT токена
        token = jwt.encode({
            'user_id': new_user.user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Токен будет действителен 1 час
        }, SECRET_KEY, algorithm='HS256')

        # Устанавливаем токен в куки
        response = make_response(redirect(url_for('account')))  # Перенаправление на страницу аккаунта
        response.set_cookie('token', token, httponly=True)  # Устанавливаем токен в куки
        return response  # Возвращаем ответ с установленным токеном

    return render_template('register.html', form=form)

@app.route('/account')
def account():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = User.query.get(data['user_id'])  # Получаем данные пользователя из базы
            return render_template('account.html', user=user)  # Передаем пользователя в шаблон
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы получить доступ к личному кабинету.', 'danger')
        return redirect(url_for('login'))  # Перенаправляем на страницу входа

@app.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = User.query.get(data['user_id'])  # Получаем данные пользователя из базы
            form = EditAccountForm(obj=user)

            if request.method == 'POST':
                # Обновляем данные пользователя
                user.first_name = request.form['first_name']
                user.last_name = request.form['last_name']
                user.phone_number = request.form['phone_number']
                user.address = request.form['address']
                user.email = request.form['email']
                db.session.commit()
                log_action(action='edit_account_success', user_id=user.user_id)

                flash('Данные аккаунта успешно обновлены!', 'success')
                return redirect(url_for('account'))

            return render_template('edit_account.html', form=form)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы получить доступ к личному кабинету.', 'danger')
        return redirect(url_for('login'))

@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    if request.method == 'POST':
        token = request.cookies.get('token')  # Получаем токен из куков
        if token:
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_id = data['user_id']  # Получаем user_id из токена

                card_number = request.form['card_number']
                card_period = request.form['card_period']
                card_cvv = request.form['card_cvv']

                # Валидация номера карты
                if not re.match(r'^\d{16}$', card_number):
                    flash('Номер карты должен содержать 16 цифр.', 'danger')
                    return redirect(url_for('add_card'))

                # Валидация срока действия
                if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', card_period):
                    flash('Срок действия карты должен быть в формате MM/YY.', 'danger')
                    return redirect(url_for('add_card'))

                # Валидация CVV
                if not re.match(r'^\d{3}$', card_cvv):
                    flash('CVV должен содержать 3 цифры.', 'danger')
                    return redirect(url_for('add_card'))

                # Если все проверки пройдены, добавляем карту
                new_card = Card(user_id=user_id, card_number=card_number, card_period=card_period, card_cvv=card_cvv)
                db.session.add(new_card)
                db.session.commit()
                flash("Карта успешно добавлена", 'success')
                return redirect(url_for('account'))  # Перенаправление на страницу аккаунта
            except jwt.ExpiredSignatureError:
                flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
                return redirect(url_for('login'))
            except jwt.InvalidTokenError:
                flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Пожалуйста, войдите в систему, чтобы добавить карту.', 'danger')
            return redirect(url_for('login'))  # Перенаправление на страницу входа

    # Если метод GET, отображаем форму добавления карты
    return render_template('add_card.html')

@app.route('/delete_card/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена

            card = Card.query.get(card_id)
            if card and card.user_id == user_id:
                db.session.delete(card)
                db.session.commit()
                flash('Карта успешно удалена.', 'success')
            else:
                flash('Не удалось удалить карту.', 'danger')
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы удалить карту.', 'danger')
        return redirect(url_for('login'))

    return redirect(url_for('account'))

@app.route('/report_problem', methods=['POST'])
def report_problem():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            problem_text = request.form['problem_text']

            # Создаем новый отчет о проблеме
            new_problem = Problem(user_id=user_id, problem_text=problem_text, is_fixed=False)
            db.session.add(new_problem)
            db.session.commit()
            flash('Проблема успешно отправлена!', 'success')
            log_action(action='report_problem_success', user_id=user_id, problem_id=new_problem.problem_id)
            return redirect(url_for('account'))
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы сообщить о проблеме.', 'danger')
        return redirect(url_for('login'))

@app.route('/catalog', methods=['GET'])
def catalog():
    categories = Category.query.all()
    selected_category_id = request.args.get('category_id', type=int)
    search_query = request.args.get('search', type=str)

    hierarchical_categories = build_hierarchy(categories)

    if selected_category_id:
        selected_category = Category.query.get(selected_category_id)
        if selected_category:
            auctions = Auction.query.filter(Auction.category_id.in_(get_all_child_ids(selected_category, hierarchical_categories))).all()
        else:
            auctions = []
    else:
        auctions = Auction.query.all()

    # Фильтрация по поисковому запросу
    if search_query:
        search_query = search_query.lower()
        auctions = [auction for auction in auctions if 
                    search_query in auction.title.lower() or 
                    search_query in auction.description.lower() or 
                    any(search_query in item.title.lower() or 
                        search_query in item.description.lower() 
                        for item in auction.items)]
        
        # Сохранение информации о поиске
        token = request.cookies.get('token')  # Получаем токен из куков
        if token:
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_id = data['user_id']  # Получаем user_id из токена

                new_search = Search(user_id=user_id, query=search_query)
                db.session.add(new_search)
                db.session.commit()
                log_action(action='search_success', user_id=user_id, search_id=new_search.search_id)
            except jwt.ExpiredSignatureError:
                flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            except jwt.InvalidTokenError:
                flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')

    return render_template('catalog.html', auctions=auctions, categories=hierarchical_categories, selected_category_id=selected_category_id)

def build_hierarchy(categories):
    """Builds a hierarchical dictionary of categories."""
    hierarchy = {}
    root_categories = []
    for category in categories:
        if category.parent_category_id is None:
            hierarchy[category.category_id] = {'name': category.name, 'children': []}
            root_categories.append(category.category_id)
        else:
            pass  # We'll add children later

    for category in categories:
        if category.parent_category_id is not None:
            parent_id = category.parent_category_id
            if parent_id in hierarchy:
                hierarchy[parent_id]['children'].append({'name': category.name, 'id': category.category_id, 'children': []})
                # Recursively build children (Not needed here because we're only one level deep)

    return [{'name':hierarchy[root]['name'], 'id':root, 'children': hierarchy[root]['children']} for root in root_categories]

def get_all_child_ids(category, hierarchy):
    ids = [category.category_id]
    for item in hierarchy:
        if item['id'] == category.category_id:
            _get_all_child_ids_recursive(item, ids)
            break

    return ids

def _get_all_child_ids_recursive(item, ids):
    for child in item['children']:
        ids.append(child['id'])
        _get_all_child_ids_recursive(child, ids)

@app.route('/auction/<int:auction_id>')
def auction(auction_id):
    auction = Auction.query.get(auction_id)
    if auction is None:
        return "Auction not found", 404

    seller = User.query.get(auction.seller_id)
    items = Item.query.filter_by(auction_id=auction_id).all()
    feedbacks = AuctionFeedback.query.filter_by(auction_id=auction_id).all()

    # Проверяем, является ли текущий пользователь продавцом аукциона
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']  # Получаем user_id из токена

            if current_user_id != auction.seller_id:
                # Добавляем запись о просмотре
                new_viewing = Viewing(auction_id=auction_id, user_id=current_user_id)
                db.session.add(new_viewing)
                db.session.commit()
                log_action(action='view_auction_success', user_id=current_user_id, auction_id=auction_id, viewing_id=new_viewing.viewing_id)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')

    return render_template('/auction.html', auction=auction, seller=seller, items=items, feedbacks=feedbacks)

@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.get(item_id)
    if item:
        bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.bid_time.desc()).all()  # Получаем все ставки для данного товара
        bid_differences = []
        previous_bid_amount = None
        
        for i in range(len(bids)):
            bid = bids[i]
            if i != len(bids)-1:
                difference = bids[i].bid_amount - bids[i+1].bid_amount
            else:
                difference = bids[i].bid_amount - item.initial_bid
                
            user = User.query.get(bid.bidder_id)
            bid_differences.append((bid, user, difference))
            previous_bid_amount = bid.bid_amount
        
        # Получаем аукцион, связанный с товаром
        auction = Auction.query.get(item.auction_id)  # Предполагается, что в Item есть поле auction_id

        return render_template('item.html', item=item, auction=auction, bid_differences=bid_differences)
    else:
        return "Item not found", 404

@app.route('/introduction/<int:auction_id>', methods=['POST', 'GET'])
def introduction(auction_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            user = User.query.get(user_id)
            
            # Проверяем, существует ли уже заявка на этот аукцион для данного пользователя
            existing_introduction = Introduction.query.filter_by(user_id=user.user_id, auction_id=auction_id).first()
            
            if existing_introduction:
                # Если заявка уже существует, проверяем ее статус
                if existing_introduction.status == 'На рассмотрении':
                    flash('Заявка находится на рассмотрении.', 'info')
                elif existing_introduction.status == 'Отклонена':
                    flash('Заявка отклонена.', 'danger')
                elif existing_introduction.status == 'Одобрена':
                    flash('Заявка одобрена.', 'success')
                return redirect(url_for('auction', auction_id=auction_id))
            
            # Получаем тип аукциона
            auction = Auction.query.get(auction_id)
            
            # Устанавливаем статус заявки в зависимости от типа аукциона
            status = 'Одобрена' if auction.auction_type == 'open' else 'На рассмотрении'
            
            new_introduction = Introduction(
                user_id=user.user_id,
                auction_id=auction_id,
                status=status 
            )
            
            db.session.add(new_introduction)
            db.session.commit()
            
            if status == 'Одобрена':
                flash('Заявка на участие успешно подана и одобрена!', 'success')
                log_action(action='introduction_success', user_id=user.user_id, auction_id=auction_id, introduction_id=new_introduction.introduction_id)
            else:
                flash('Заявка на участие успешно подана и находится на рассмотрении!', 'success')
                log_action(action='introduction_success', user_id=user.user_id, auction_id=auction_id, introduction_id=new_introduction.introduction_id)
            
            return redirect(url_for('auction', auction_id=auction_id))
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы зарегистрироваться на участие в аукционе.', 'danger')
        return redirect(url_for('login'))

@app.route('/make_bid/<int:item_id>', methods=['POST', 'GET'])
def make_bid(item_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            user = User.query.get(user_id)
            item = Item.query.get(item_id)

            # Получаем статус пользователя для данного аукциона
            introduction = Introduction.query.filter_by(user_id=user.user_id, auction_id=item.auction_id).first()

            if introduction:
                if introduction.status == 'Одобрена':
                    # Отображаем форму для создания ставки
                    min_required_bid = None  # Инициализируем переменную
                    if request.method == 'POST':
                        bid_amount = request.form.get('bid_amount', type=float)

                        # Проверяем минимальную ставку
                        max_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar()
                        min_bid = max_bid if max_bid is not None else item.initial_bid
                        min_required_bid = min_bid + item.min_difference_bid

                        if bid_amount < min_required_bid:
                            flash(f'Ставка должна быть не менее {min_required_bid}.', 'danger')
                        else:
                            new_bid = Bid(item_id=item_id, bidder_id=user.user_id, bid_amount=bid_amount)
                            db.session.add(new_bid)
                            db.session.commit()
                            flash('Ставка успешно сделана!', 'success')
                            log_action(action='make_bid_success', user_id=user.user_id, item_id=item_id, bid_id=new_bid.bid_id)
                            return redirect(url_for('item', item_id=item_id))

                    # Если это GET-запрос, вычисляем минимально допустимую ставку
                    if min_required_bid is None:
                        max_bid = db.session.query(db.func.max(Bid.bid_amount)).filter_by(item_id=item_id).scalar()
                        min_bid = max_bid if max_bid is not None else item.initial_bid
                        min_required_bid = min_bid + item.min_difference_bid

                    return render_template('make_bid.html', item=item, min_required_bid=min_required_bid)

                elif introduction.status == 'На рассмотрении':
                    flash('Ваша заявка находится на рассмотрении, вы пока не можете делать ставки.', 'warning')
                    return redirect(url_for('item', item_id=item_id))

                elif introduction.status == 'Отклонена':
                    flash('Ваша заявка на участие в аукционе отклонена.', 'danger')
                    return redirect(url_for('item', item_id=item_id))
                else:
                    return redirect(url_for('/'))

            else:
                flash('Вы не участвуете в этом аукционе.', 'danger')
                return redirect(url_for('item', item_id=item_id))
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы сделать ставку.', 'danger')
        return redirect(url_for('login'))

@app.route('/participating', methods=['GET'])
def participating():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            user = User.query.get(user_id)
            
            # Получаем все аукционы, в которых пользователь участвует с статусом 'accepted'
            accepted_auctions_query = (
                db.session.query(Auction)
                .join(Introduction)
                .filter(Introduction.user_id == user.user_id, Introduction.status == 'Одобрена')
            )

            # Получаем фильтр из параметров запроса
            filter_type = request.args.get('filter', 'all')

            if filter_type == 'active':
                auctions = accepted_auctions_query.filter(Auction.status == 'active').all()
            elif filter_type == 'ended':
                auctions = accepted_auctions_query.filter(Auction.status == 'ended').all()
            elif filter_type == 'pending_or_rejected':
                auctions = (
                    db.session.query(Auction)
                    .join(Introduction)
                    .filter(
                        Introduction.user_id == user.user_id,
                        Introduction.status.in_(['На рассмотрении', 'Отклонена'])
                    )
                ).all()
            else:
                auctions = accepted_auctions_query.all()

            return render_template('participating.html', auctions=auctions, filter_type=filter_type)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы просмотреть свои аукционы.', 'danger')
        return redirect(url_for('login'))

@app.route('/my_auctions', methods=['GET'])
def my_auctions():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            # Получаем все аукционы, где пользователь является продавцом
            auctions_query = Auction.query.filter(Auction.seller_id == user_id)

            # Получаем фильтр из параметров запроса
            filter_type = request.args.get('filter', 'all')

            if filter_type == 'active':
                auctions = auctions_query.filter(Auction.status == 'active').order_by(Auction.start_time.desc()).all()
            elif filter_type == 'ended':
                auctions = auctions_query.filter(Auction.status == 'ended').order_by(Auction.start_time.desc()).all()
            else:
                auctions = auctions_query.order_by(Auction.start_time.desc()).all()

            return render_template('my_auctions.html', auctions=auctions, filter_type=filter_type)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы просмотреть свои аукционы.', 'danger')
        return redirect(url_for('login'))

@app.route('/edit_auction/<int:auction_id>', methods=['GET', 'POST'])
def edit_auction(auction_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            auction = Auction.query.get(auction_id)
            
            if auction is None:
                flash('Аукцион не найден.', 'danger')
                return redirect(url_for('my_auctions'))

            if auction.seller_id != user_id:
                flash('У вас нет прав для редактирования этого аукциона.', 'danger')
                return redirect(url_for('my_auctions'))

            categories = Category.query.all()

            if request.method == 'POST':
                auction.title = request.form.get('title')
                auction.description = request.form.get('description')
                auction.start_time = datetime.datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
                auction.end_time = datetime.datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
                auction.category_id = request.form.get('category_id')
                auction.auction_type = request.form.get('auction_type')

                db.session.commit()
                flash('Аукцион успешно обновлён!', 'success')
                log_action(action='edit_auction_success', user_id=user_id, auction_id=auction_id)
                return redirect(url_for('my_auctions'))

            items = Item.query.filter_by(auction_id=auction_id).all()
            return render_template('edit_auction.html', auction=auction, items=items, categories=categories)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы просмотреть свои аукционы.', 'danger')
        return redirect(url_for('login'))

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            item = Item.query.get(item_id)
            
            if item is None:
                flash('Лот не найден.', 'danger')
                return redirect(url_for('my_auctions'))

            auction = Auction.query.get(item.auction_id)
            if auction.seller_id != user_id:
                flash('У вас нет прав для редактирования этого лота.', 'danger')
                return redirect(url_for('my_auctions'))

            # Извлекаем существующие фотографии и видео
            existing_photos = ItemPhoto.query.filter_by(item_id=item_id).all()
            existing_videos = ItemVideo.query.filter_by(item_id=item_id).all()

            if request.method == 'POST':
                item.title = request.form.get('title')
                item.description = request.form.get('description')
                item.start_time = datetime.datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
                item.end_time = datetime.datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
                item.initial_bid = request.form.get('initial_bid')
                item.min_difference_bid = request.form.get('min_difference_bid')

                # Обработка загруженных фотографий
                if 'photos' in request.files:
                    photos = request.files.getlist('photos')
                    for photo in photos:
                        if photo and allowed_file(photo.filename):
                            unique_filename = generate_unique_filename(photo.filename)
                            photo_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                            photo.save(photo_path)
                            item_photo = ItemPhoto(item_id=item.item_id, url=unique_filename)
                            db.session.add(item_photo)
                            log_action(action='upload_item_photo_success', user_id=user_id, item_id=item_id, item_photo_id=item_photo.photo_id)

                # Обработка загруженного видео
                if 'video' in request.files:
                    videos = request.files['video']
                    for video in videos:
                        if video and allowed_file(video.filename):
                            unique_filename = generate_unique_filename(video.filename)
                            video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                            video.save(video_path)
                            item_video = ItemVideo(item_id=item.item_id, url=unique_filename)
                            db.session.add(item_video)
                            log_action(action='upload_item_video_success', user_id=user_id, item_id=item_id, item_video_id=item_video.video_id)

                db.session.commit()
                flash('Лот успешно обновлён!', 'success')
                
                # Логируем успешное редактирование лота
                log_action(action='edit_item_success', user_id=user_id, item_id=item_id)
                return redirect(url_for('my_auctions'))
            return render_template('edit_item.html', item=item, auction=auction, existing_photos=existing_photos, existing_videos=existing_videos)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            log_action(action='edit_item_failure', reason='token_expired', item_id=item_id)
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            log_action(action='edit_item_failure', reason='invalid_token', item_id=item_id)
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы просмотреть свои лоты.', 'danger')
        log_action(action='edit_item_failure', reason='user_not_logged_in', item_id=item_id)
        return redirect(url_for('login'))

@app.route('/create_auction', methods=['GET', 'POST'])
def create_auction():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена

            if request.method == 'POST':
                title = request.form.get('title')
                description = request.form.get('description')
                start_time = datetime.datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
                end_time = datetime.datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
                category_id = request.form.get('category_id')
                auction_type = request.form.get('auction_type')

                # Создаем новый аукцион
                new_auction = Auction(
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    seller_id=user_id,
                    category_id=category_id,
                    auction_type=auction_type
                )

                db.session.add(new_auction)
                db.session.commit()
                flash('Аукцион успешно создан!', 'success')
                log_action(action='create_auction_success', user_id=user_id, auction_id=new_auction.auction_id)
                return redirect(url_for('edit_auction', auction_id=new_auction.auction_id))

            # Получаем список категорий для отображения в форме
            categories = Category.query.all()
            return render_template('create_auction.html', categories=categories)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы создать аукцион.', 'danger')
        return redirect(url_for('login'))

@app.route('/create_item/<int:auction_id>', methods=['GET', 'POST'])
def create_item(auction_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена

            if request.method == 'POST':
                title = request.form.get('title')
                description = request.form.get('description')
                start_time = datetime.datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
                end_time = datetime.datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
                initial_bid = request.form.get('initial_bid', type=float)
                min_difference_bid = request.form.get('min_difference_bid', type=float)

                # Создаем новый лот
                new_item = Item(
                    auction_id=auction_id,
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    initial_bid=initial_bid,
                    min_difference_bid=min_difference_bid,
                    status='active'
                )

                db.session.add(new_item)
                db.session.commit()
                flash('Лот успешно создан!', 'success')
                log_action(action="create_item_success", user_id=user_id, auction_id=auction_id, item_id=new_item.item_id)
                return redirect(url_for('edit_item', item_id=new_item.item_id))
            
            # Получаем информацию о выбранном аукционе
            auction = Auction.query.get(auction_id)
            return render_template('create_item.html', auction=auction)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы создать лот.', 'danger')
        return redirect(url_for('login'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    # Получаем расширение файла
    ext = filename.rsplit('.', 1)[1].lower()
    # Генерируем уникальное имя файла с использованием временной метки
    unique_filename = f"{int(time.time())}_{secure_filename(filename)}"
    return f"{unique_filename}.{ext}"

@app.route('/submit_feedback/<int:auction_id>', methods=['POST'])
def submit_feedback(auction_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            auction = Auction.query.get(auction_id)
            if auction.seller_id == user_id:
                flash("Вы не можете оставлять отзыв на свой аукцион.", "error")
                return redirect(url_for('auction', auction_id=auction_id))

            existing_feedback = AuctionFeedback.query.filter_by(auction_id=auction_id, user_id=user_id).first()
            if existing_feedback:
                flash("Вы уже оставляли отзыв на этот аукцион.", "error")
                return redirect(url_for('auction', auction_id=auction_id))

            dignities = request.form['dignities']
            disadvantages = request.form['disadvantages']
            comment = request.form['comment']
            stars_count = request.form['stars_count']

            new_feedback = AuctionFeedback(
                auction_id=auction_id,
                user_id=user_id,
                dignities=dignities,
                disadvantages=disadvantages,
                comment=comment,
                stars_count=stars_count
            )

            # Обработка загруженных фото
            if 'photos' in request.files:
                photos = request.files.getlist('photos')
                for photo in photos:
                    if photo and allowed_file(photo.filename):
                        unique_filename = generate_unique_filename(photo.filename)
                        photo_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        photo.save(photo_path)
                        feedback_photo = FeedbackPhoto(feedback_id=new_feedback.feedback_id, url=unique_filename)
                        new_feedback.photos.append(feedback_photo)
                        log_action(action='upload_feedback_photo_success', user_id=user_id, auction_id=auction_id, feedback_photo_id=feedback_photo.photo_id)

            # Обработка загруженного видео
            if 'video' in request.files:
                video = request.files['video']
                if video and allowed_file(video.filename):
                    unique_filename = generate_unique_filename(video.filename)
                    video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    video.save(video_path)
                    feedback_video = FeedbackVideo(feedback_id=new_feedback.feedback_id, url=unique_filename)
                    new_feedback.videos.append(feedback_video)
                    log_action(action='upload_feedback_video_success', user_id=user_id, auction_id=auction_id, feedback_video_id=feedback_video.video_id)

            # Сохранение отзыва в базе данных
            db.session.add(new_feedback)
            db.session.commit()
            log_action(action='submit_feedback_success', user_id=user_id, auction_id=auction_id, feedback_id=new_feedback.feedback_id)

            flash("Ваш отзыв был успешно отправлен!", "success")
            return redirect(url_for('auction', auction_id=auction_id))
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы оставить отзыв.', 'danger')
        return redirect(url_for('login'))

@app.route('/user/chats', methods=['GET'])
def user_chats():
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            # Получаем все сообщения, отправленные и полученные пользователем
            sent_messages = Message.query.filter_by(sender_id=user_id).all()
            received_messages = Message.query.filter_by(recipient_id=user_id).all()

            # Получаем все заявки пользователя на участие в аукционах
            user_introductions = Introduction.query.filter_by(user_id=user_id).all()

            # Получаем все аукционы, в которых пользователь является организатором
            seller_auctions = Auction.query.filter_by(seller_id=user_id).all()

            # Получаем все заявки на аукционы, в которых пользователь является организатором
            seller_introductions = Introduction.query.filter(Introduction.auction_id.in_([auction.auction_id for auction in seller_auctions])).all()

            # Получаем информацию о пользователях, которые отправили заявки
            users_for_seller_introductions = {intro.introduction_id: User.query.get(intro.user_id) for intro in seller_introductions}

            # Создаем словарь для хранения чатов
            chats = {}

            # Обрабатываем отправленные сообщения
            for message in sent_messages:
                if message.recipient_id not in chats:
                    chats[message.recipient_id] = {
                        'username': message.recipient.username,
                        'last_message': message,
                        'user_id': message.recipient_id
                    }
                else:
                    if message.created_at > chats[message.recipient_id]['last_message'].created_at:
                        chats[message.recipient_id]['last_message'] = message

            # Обрабатываем полученные сообщения
            for message in received_messages:
                if message.sender_id not in chats:
                    chats[message.sender_id] = {
                        'username': message.sender.username,
                        'last_message': message,
                        'user_id': message.sender_id
                    }
                else:
                    if message.created_at > chats[message.sender_id]['last_message'].created_at:
                        chats[message.sender_id]['last_message'] = message

            # Сортируем чаты по времени последнего сообщения
            sorted_chats = sorted(chats.values(), key=lambda x: x['last_message'].created_at, reverse=True)

            return render_template('user_chats.html', 
                                   chats=sorted_chats,
                                   user_introductions=user_introductions,
                                   seller_introductions=seller_introductions,
                                   users_for_seller_introductions=users_for_seller_introductions)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы посмотреть чаты.', 'danger')
        return redirect(url_for('login'))

@app.route('/approve_introduction/<int:introduction_id>', methods=['POST'])
def approve_introduction(introduction_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            # Получаем заявку по ID
            introduction = Introduction.query.get(introduction_id)
            
            if introduction:
                # Проверяем, является ли текущий пользователь организатором аукциона
                if introduction.auction.seller_id == user_id:
                    # Обновляем статус на "Одобрено"
                    introduction.status = 'Одобрена'
                    db.session.commit()
                    flash('Заявка успешно одобрена!', 'success')
                    log_action(action='approve_introduction_success', introduction_id=introduction_id)
                else:
                    flash('У вас нет прав для одобрения этой заявки.', 'danger')
            else:
                flash('Заявка не найдена.', 'danger')
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы одобрить заявку.', 'danger')
        return redirect(url_for('login'))

    return redirect(url_for('user_chats'))  # Перенаправляем на страницу чатов

@app.route('/decline_introduction/<int:introduction_id>', methods=['POST'])
def decline_introduction(introduction_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']  # Получаем user_id из токена
            
            # Получаем заявку по ID
            introduction = Introduction.query.get(introduction_id)
            
            if introduction:
                # Проверяем, является ли текущий пользователь организатором аукциона
                if introduction.auction.seller_id == user_id:
                    # Обновляем статус на "Отклонена"
                    introduction.status = 'Отклонена'
                    db.session.commit()
                    flash('Заявка успешно отклонена!', 'success')
                    log_action(action='decline_introduction_success', introduction_id=introduction_id)
                else:
                    flash('У вас нет прав для отклонения этой заявки.', 'danger')
            else:
                flash('Заявка не найдена.', 'danger')
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы отклонить заявку.', 'danger')
        return redirect(url_for('login'))

    return redirect(url_for('user_chats'))  # Перенаправляем на страницу чатов

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']  # Получаем user_id текущего пользователя
            
            # Получаем информацию о пользователе
            user = User.query.get(user_id)

            # Проверяем, существует ли пользователь и не удалён ли он
            if user is None or user.is_deleted:
                return render_template('user_profile.html', user=None)

            # Получаем список аукционов, организованных пользователем
            auctions = Auction.query.filter_by(seller_id=user_id).all()

            # Отображаем информацию о пользователе и его аукционах
            return render_template('user_profile.html', user=user, auctions=auctions)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы просмотреть профиль пользователя.', 'danger')
        return redirect(url_for('login'))

@app.route('/chat/<int:user_id>')
def chat(user_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']  # Получаем user_id текущего пользователя

            # Проверяем, пытается ли пользователь открыть чат с самим собой
            if current_user_id == user_id:
                flash('Вы не можете открыть чат с самим собой.', 'warning')
                return redirect(url_for('account'))

            # Получаем информацию о пользователе
            user = User.query.get(user_id)

            # Проверяем, существует ли пользователь и не удалён ли он
            if user is None or user.is_deleted:
                return render_template('user_profile.html', user=None)

            # Получаем сообщения между текущим пользователем и выбранным пользователем
            messages = Message.query.filter(
                ((Message.sender_id == current_user_id) & (Message.recipient_id == user_id)) |
                ((Message.sender_id == user_id) & (Message.recipient_id == current_user_id))
            ).order_by(Message.created_at).all()

            return render_template('chat.html', user=user, messages=messages)
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы открыть чат.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/send_message/<int:recipient_id>', methods=['POST'])
def send_message(recipient_id):
    token = request.cookies.get('token')  # Получаем токен из куков
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']  # Получаем user_id текущего пользователя

            # Проверяем, пытается ли пользователь отправить сообщение самому себе
            if current_user_id == recipient_id:
                flash('Вы не можете отправить сообщение самому себе.', 'warning')
                return redirect(url_for('account'))

            message_content = request.form['message']

            # Создаем новое сообщение
            new_message = Message(sender_id=current_user_id, recipient_id=recipient_id, message=message_content)
            db.session.add(new_message)
            db.session.commit()
            log_action(action='send_message_success', user_id=current_user_id, message_id=new_message.message_id)
            return redirect(url_for('chat', user_id=recipient_id))
        except jwt.ExpiredSignatureError:
            flash('Токен истек. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Неверный токен. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Пожалуйста, войдите в систему, чтобы открыть чат.', 'danger')
        return redirect(url_for('login'))
    
if __name__ == '__main__':
    #create_tables()  # Создание таблиц
    app.run(debug=True)


