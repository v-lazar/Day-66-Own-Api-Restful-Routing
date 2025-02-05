import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, select

TopSecretAPIKey = "N6YpihjkPmdf>3U?ZY8#-9_DTj,2awoU}-Jfc.vWJfaToLdMnBKV0:9VWV5b"

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            ## Create a new dictionary entry;
            ## where the key is the name of the column
            ## and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        ## Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    # return jsonify(
    #     cafe = {
    #         "id": random_cafe.id,
    #         "name": random_cafe.name,
    #         "map_url": random_cafe.map_url,
    #         "img_url": random_cafe.img_url,
    #         "location": random_cafe.location,
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls":random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #
    #     }
    # )
    ## Or
    return jsonify(cafe=random_cafe.to_dict())



@app.route("/all", methods=['GET'])
def get_all_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])



@app.route("/search", methods=['GET', 'POST'])
def search():
        query_location = request.args.get('loc').capitalize()
        result = db.session.execute(select(Cafe).where(Cafe.location == query_location))
        all_cafes = result.scalars().all()
        if all_cafes:
            return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
        else:
            return jsonify(error={"Not found": "Sorry, we don't have a cafe at that location."}), 404

# HTTP POST - Create Record

@app.route("/add", methods=['POST'])
def add():
    new_entry= Cafe(
        name = request.form.get('name'),
        map_url = request.form.get('map_url'),
        img_url = request.form.get('img_url'),
        location = request.form.get('location'),
        seats = request.form.get('seats'),
        has_toilet = bool(request.form.get('has_toilet')),
        has_wifi = bool(request.form.get('has_wifi')),
        has_sockets = bool(request.form.get('has_sockets')),
        can_take_calls = bool(request.form.get('can_take_calls')),
        coffee_price = request.form.get('coffee_price')
        )

    db.session.add(new_entry)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get('new_price')

    cafe_to_update = db.session.get(Cafe, cafe_id)


    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete(cafe_id):

    api_key = request.args.get('api-key')

    if api_key == TopSecretAPIKey:
        cafe_to_delete = db.session.get(Cafe, cafe_id)

        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Entry deleted from the database,"}), 200

        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

    else:
        return jsonify(response={"error": "Not allowed. Missing or incorrect API Key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
