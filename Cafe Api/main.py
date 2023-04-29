from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

@app.route("/random", methods=["GET"])
def random():
    number_of_rows = db.session.query(Cafe).count()
    random_id = randint(1, number_of_rows)
    random_cafe = Cafe.query.get(random_id)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route("/all")
def all_():
    cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in cafes:
        cafe_dict = {"id": cafe.id, "name": cafe.name, "map_url": cafe.map_url,
                     "img_url": cafe.img_url,
                     "location": cafe.location, "has_sockets": cafe.has_sockets,
                     "has_toilet": cafe.has_toilet, "has_wifi": cafe.has_wifi,
                     "can_take_calls": cafe.can_take_calls, "seats": cafe.seats,
                     "coffee_price": cafe.coffee_price}
        cafe_list.append(cafe_dict)
    all_cafes = {"cafes": cafe_list}
    all_cafes_json = jsonify(cafes=all_cafes["cafes"])
    return all_cafes_json


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("location")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe={
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price,
        })
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add():
    data = request.form
    new_cafe = Cafe(name=data.get("name"), map_url=data.get("map_url"),
                    img_url=data.get("img_url"),
                    location=data.get("location"), has_sockets=int(data.get("has_sockets")),
                    has_toilet=int(data.get("has_toilet")), has_wifi=int(data.get("has_wifi")),
                    can_take_calls=int(data.get("can_take_calls")), seats=data.get("seats"),
                    coffee_price=data.get("coffee_price"))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Added a new cafe successfully!"})


#  HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:id_>", methods=["PATCH"])
def update_price(id_):
    cafe_to_update = Cafe.query.get(id_)
    if cafe_to_update:
        query_price = request.args.get("coffee_price")
        cafe_to_update.coffee_price = query_price
        db.session.commit()
        return jsonify({"success": f"Cafe with the id of {id_} was updated!"})
    else:
        return jsonify(error={"Not Found": f"Sorry, the cafe with an id of {id_} was not found in the database."})

#    HTTP DELETE - Delete Record


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    api_key = request.args.get("api_key")
    if cafe_to_delete and api_key == "MySuperSecretApiKey":
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify({"success": f"Cafe deleted!"})
    else:
        return jsonify(error={"Not Found": f"Sorry, there is no cafe with an id of {cafe_id}."})

if __name__ == '__main__':
    app.run(debug=True)
