from flask import Flask, render_template,  request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import stripe

stripe.api_key = "dsdsdsdsdsadae3223"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
app.secret_key = '2sDf43rsfsd3rSD4gdfsd45.,werwer' 
db = SQLAlchemy(app)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

cart = []

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    img_url = db.Column(db.String(255))
    product_price = db.Column(db.Integer)
    description = db.Column(db.String(255))
    full_description = db.Column(db.String(255))



@app.route('/products')
def list_products():
    products = Product.query.all()
    return render_template('products.html', products=products)


@app.route('/product/<int:product_id>')
def show_product(product_id):
    product = Product.query.get(product_id)
    return render_template('product_details.html', product=product)


login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('list_products'))
        else:
            flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('list_products'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # Obtén el producto por ID y agrégalo al carrito
    product = Product.query.get(product_id)
    if product:
        cart.append(product)
    return redirect(url_for('list_products'))

@app.route('/cart')
def view_cart():
    total_amount = sum(int(product.product_price) for product in cart)
    return render_template('cart.html', cart=cart, total_amount=total_amount)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            token = request.form['stripeToken']
            
         
            total_amount = 0
            for product in cart:
                total_amount += int(product.product_price)

       
            charge = stripe.Charge.create(
                amount=total_amount * 100, 
                currency="usd",
                source=token,
                description="Pago de productos"
            )

        
            cart.clear()

            flash('Pago exitoso. Gracias por tu compra', 'success')
            return redirect(url_for('list_products'))

        except stripe.error.CardError as e:
            flash(f'Error en la tarjeta, verifica tu tarjeta: {e.error.message}', 'error')
            return redirect(url_for('cart'))
        except Exception as e:
            flash(f'Error al procesar el pago, reintente en unos minutos: {str(e)}', 'error')
            return redirect(url_for('cart'))
    return render_template('checkout.html')


    return render_template('checkout.html')
if __name__ == '__main__':
    app.run(debug=True)