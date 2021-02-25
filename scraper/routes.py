import json
from scraper import app, db
from sqlalchemy import desc
from scraper.forms import ProductForm, LoginForm, EditProfileForm
from scraper.models import User, Product
from werkzeug.urls import url_parse
from flask_login import current_user, login_required, login_user, logout_user
from flask import render_template, flash, redirect, url_for, request
import requests


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ProductForm()
    if form.is_submitted():
        if validate_url(form.url.data):
            product = Product.query.filter_by(url=form.url.data).first()
            if product is None:
                product = Product(url=form.url.data)
                db.session.add(product)
                db.session.commit()
                flash(f"URL Added: {form.url.data}")
                form.url.data = ''
            else:
                flash(f"URL Already Exists")
        else:
            flash(
                "URL Invalid - Must being with \'https://www.homedepot.com/p/\'")

    products = Product().query.order_by(desc(Product.created)).all()
    current_user.updates_available = False
    db.session.commit()
    return render_template('index.html', form=form, products=products)


def validate_url(url):
    start = "https://www.homedepot.com/p/"
    if url[:len(start)] == start:
        return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
@login_required
def update():
    if request.method == 'POST':
        try:
            return str(current_user.updates_available)
        except:
            return False
    return False


@app.route('/scrapeall', methods=['GET', 'POST'])
@login_required
def scraperall():
    send_scrapyd()
    return redirect(url_for('index'))


@app.route('/scrape/<product_id>')
@login_required
def scrape(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is not None:
        send_scrapyd(product)
    else:
        flash(f"Product does not exist, cannot scrape")
    return redirect(url_for('index'))


def send_scrapyd(product=None):
    url = 'http://localhost:6800/schedule.json'
    data = {
        'project': 'scraper',
        'spider': 'home_depot_spider'
    }

    if product is not None:
        data['url'] = product.url

    response = requests.post(url, data=data)

    if response.status_code == 200:
        flash(f"Data sent to scraper!")
    else:
        flash(f"There was an error running the scraper!")


@app.route('/toggle/<product_id>')
@login_required
def toggle(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        flash(f'Product ID not found')
    else:
        product.enabled = not product.enabled
        db.session.commit()
        flash(
            f"Product ID [{product.title}] {'enabled' if product.enabled else 'disabled'}")
    return redirect(url_for('index'))


@app.route('/delete/<product_id>')
@login_required
def delete(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is not None:
        db.session.delete(product)
        db.session.commit()
        flash(f"Product deleted")
    else:
        flash(f"Product could not be found")
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data

        if not current_user.email == form.email.data:
            current_user.email = form.email.data
            # send email to admin informing new email for
            # notifications ie add to mail whitelist
            # > could this be an API call?

        if len(form.password.data) > 0:
            current_user.password = form.password.data
            current_user.password2 = form.password2.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)
