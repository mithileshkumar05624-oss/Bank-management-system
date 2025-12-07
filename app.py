from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    balance = db.Column(db.Integer, default=0)

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            return False
        else:
            self.balance -= amount
            return True



@app.route('/')
def home():
    accounts = Bank.query.all()
    return render_template("index.html", banks=accounts)


@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == "POST":
        acc_no = int(request.form["account_number"])
        name = request.form["full_name"]
        phone = request.form["phone_number"]

        
        obj = Bank(account_number=acc_no, full_name=name, phone_number=phone, balance=0)
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("create.html")


@app.route('/deposit/<int:acc_no>', methods=["GET", "POST"])
def deposit(acc_no):
    obj = Bank.query.filter_by(account_number=acc_no).first()
    if obj:
        if request.method == "POST":
            amount = int(request.form["amount"])
            obj.deposit(amount)
            db.session.commit()
            return redirect(url_for("home"))
        return render_template("deposit.html", account=obj)
    return "Account not found!"


@app.route('/withdraw/<int:acc_no>', methods=["GET", "POST"])
def withdraw(acc_no):
    obj = Bank.query.filter_by(account_number=acc_no).first()
    if obj:
        if request.method == "POST":
            amount = int(request.form["amount"])
            if obj.withdraw(amount):
                db.session.commit()
                return redirect(url_for("home"))
            else:
                return "Insufficient Balance!"
        return render_template("withdraw.html", account=obj)
    return "Account not found!"


@app.route('/transfer', methods=["GET", "POST"])
def transfer():
    if request.method == "POST":
        from_acc = int(request.form["from_account"])
        to_acc = int(request.form["to_account"])
        amount = int(request.form["amount"])

        from_obj = Bank.query.filter_by(account_number=from_acc).first()
        to_obj = Bank.query.filter_by(account_number=to_acc).first()

        if from_obj and to_obj:
            if from_obj.withdraw(amount):
                to_obj.deposit(amount)
                db.session.commit()
                return redirect(url_for("home"))
            else:
                return "Insufficient Balance!"
        return "One or both accounts not found!"
    return render_template("transfer.html")




with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
