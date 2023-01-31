from flask import Flask,render_template,redirect,url_for,flash,request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from Forms import login_form,regester
from flask_login import UserMixin,login_user,logout_user,LoginManager,current_user,login_required
from werkzeug.security import check_password_hash,generate_password_hash
import os
import stripe


publish_key="pk_test_51M5kAHIzx1auNHnjZkLpP4xeXZblV7l9l28tWjBUHtYPlKAaoRT6SzD382wM8HuXul3GZ10L2nVUAO0n0x4Pbb5G00cKdEh7sc"
stripe.api_key="sk_test_51M5kAHIzx1auNHnjfHdtVNaEV5W7KsBHaCzBVlIS9FtTeVz09X4ECk4EugmA6snVkiuEg5ecpPMfXBInuygg2Q8H00jqr2guBw"
app=Flask(__name__)
Bootstrap(app)



app.config["SECRET_KEY"]="nckjgfsggiuhgiushgirug"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)





class products_db(db.Model):

    id= db.Column(db.Integer,primary_key=True)
    p_name=db.Column(db.String,nullable=False)
    p_info=db.Column(db.String,nullable=False)
    p_price=db.Column(db.String,nullable=False)
    p_gender=db.Column(db.String,nullable=False)
    p_image=db.Column(db.String,nullable=False)

class User(db.Model,UserMixin):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False,unique=True)
    email = db.Column(db.String, nullable=False,unique=True)
    password = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    shelf = db.Column(db.String)




login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route("/payment",methods=["POST"])
@login_required
def payment():
    price=request.form.get("price")
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description=f'{current_user.username} Basket',
        amount=price,
        currency='sar',
    )
    return redirect(url_for("thanks",user=current_user.id))

@app.route("/thanks")
@login_required
def thanks():
    user=User.query.get(request.args.get("user"))
    user.shelf=None
    db.session.commit()
    return render_template("thanks.html")






@app.route("/")
def home():
    men_products=products_db.query.filter_by(p_gender="men").all()
    women_products = products_db.query.filter_by(p_gender="women").all()
    return render_template('index.html',men_items=men_products,women_items=women_products)

@app.route("/login",methods=["POST","GET"])
def login():
    form=login_form()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for("home", user=user.username))
            else:
                flash("wrong Password")
        else:
            flash("Email not Exist")

    return render_template("login.html",form=form)

@app.route("/new_account",methods=["POST","GET"])
def new_account():
    form=regester()
    if request.method=="POST":
        if form.validate_on_submit():
            if not User.query.filter_by(email=form.email.data).first() and not User.query.filter_by(username=form.username.data).first():
                if not User.query.filter_by(number=form.phone.data).first():
                    if form.password.data==form.password_2.data:
                        h_password=generate_password_hash(form.password.data,method="pbkdf2:sha256",salt_length=8)
                        new_user=User(username=form.username.data,
                                      email = form.email.data,
                                      password =h_password,
                                      number =form.phone.data)
                        db.session.add(new_user)
                        db.session.commit()
                        login_user(new_user)
                        return redirect(url_for("home",user=form.username.data))
                    else:
                        flash("Password Not Match")
                else:
                    flash("You have account already")
            else:
                flash("You have account already")

    return render_template("new_account.html",form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/closet")
def item():
    item_id=request.args.get("id")
    item = products_db.query.get(item_id)
    user_name=request.args.get("user")
    return render_template("item_page.html",user_name=user_name,item_id=item_id,item=item)

@app.route("/women")
def women():
    all_women = products_db.query.filter_by(p_gender="women").all()
    return render_template("women.html",women=all_women)

@app.route("/men")
def men():
    all_men=products_db.query.filter_by(p_gender="men").all()
    return render_template("men.html",men=all_men)

@app.route("/add_to_shelf")
@login_required
def buy():

    user=request.args.get("user")
    user=User.query.filter_by(username=user).first()

    user.shelf=f"{user.shelf},{request.args.get('id')}"
    db.session.commit()
    return redirect(url_for(request.referrer))

@app.route("/shelf")
@login_required
def shelf():
    user=User.query.filter_by(username=request.args.get("user")).first()
    if user.shelf!=None:
        all_items=user.shelf.split(",")


        if "None" in all_items:
            all_items.remove("None")
        elif '' in all_items:
            all_items.remove('')


        price=0
        all_products={}
        for i in all_items:
            item=products_db.query.get(i)
            all_products[item.p_image]=item.p_price.split(' ')[1]

        num = len(all_products)
        for item in all_products:
            price+=float(all_products[item])


    else:
        all_products=[]
        num=0





    return render_template("basket.html",items=all_products,num=num,price=price)


@app.route("/delete")
@login_required
def delete():
    item=products_db.query.filter_by(p_image=request.args.get("item")).first()
    user=User.query.filter_by(username=request.args.get("user")).first()
    user_items=user.shelf.split(',')
    user_items.remove(str(item.id))
    items=",".join(user_items)
    user.shelf=items
    db.session.commit()
    return redirect(url_for("shelf",user=user.username))







if __name__=="__main__":
    app.run(debug=True)
