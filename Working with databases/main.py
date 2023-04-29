from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pc.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Pc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pc_name = db.Column(db.String(250), unique=True, nullable=False)
    pc_brand = db.Column(db.String(250), nullable=False)


db.create_all()


@app.route("/", methods=["POST", "GET"])
def home():
    all_pc = db.session.query(Pc).all()
    if request.method == "POST":
        data = request.form
        new_pc = Pc(pc_name=data["pc_name"], pc_brand=data["pc_brand"])
        db.session.add(new_pc)
        try:
            db.session.commit()
        except IntegrityError:
            return "<h1>You have specified a duplicate pc name.</h1>" \
                   "<p>Please return to the <a href='/'>home</a> page to correct it.</p>"
        return redirect(url_for('home'))
    return render_template("add_pc.html", all_pc=all_pc)


@app.route("/delete")
def delete():
    pc_id = request.args.get('id')
    # DELETE A RECORD BY ID
    pc_to_delete = Pc.query.get(pc_id)
    db.session.delete(pc_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        pc_id = request.form.get('id')
        pc_to_update = Pc.query.get(pc_id)
        pc_to_update.pc_brand = request.form["brand"]
        db.session.commit()
        return redirect(url_for("home"))
    pc_id = request.args.get('id')
    pc_selected = Pc.query.get(pc_id)
    return render_template("edit.html", pc=pc_selected)


if __name__ == "__main__":
    app.run(debug=True)
