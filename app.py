from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# *Init Flask
app = Flask(__name__)
# *Create a var to change the DB based upon if its development or production
ENV = 'dev'

if ENV == "dev":
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:EmptyObject=False!69@localhost/challengerDB'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
db = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    artwork = db.Column(db.String(1000), nullable=False)
    gif = db.Column(db.String(1000))
    status = db.Column(db.Boolean, default=False)

    def __init__(self, name, artwork, gif, status=False):
        self.name = name
        self.artwork = artwork
        self.gif = gif
        self.status = status

    def __repr__(self):
        return f" Game: {self.id}, {self.name} "


class GameSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'artwork', 'gif', 'status')


game_schema = GameSchema()
games_schema = GameSchema(many=True)

# ! Challenges


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.String(1000))
    type = db.Column(db.String(100))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    def __repr__(self):
        return f" Game: {self.id}, {self.contents} "

    def __init__(self, contents, type, game_id):
        self.contents = contents
        self.type = type
        self.game_id = game_id


class ChallengeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'contents', 'type', 'game_id')


challenge_schema = ChallengeSchema()
challenges_schema = ChallengeSchema(many=True)


# class Queue(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100))
#     status = db.Column(db.String(100))
#     game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
#     challege_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))

#     def __init__(self, username, status, game_id, challege_id):
#         self.username = username
#         self.status = status
#         self.game_id = game_id
#         self.challege_id = challege_id


# class QueueSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'username', 'status', 'game_id', 'challege_id')


# queue_schema = QueueSchema()
# queues_schema = QueueSchema(many=True)


# Create a Game
@app.route('/game', methods=['POST'])
def createGame():
    name = request.json['name']
    artwork = request.json['artwork']
    gif = request.json['gif']

    newGame = Game(name, artwork, gif)

    db.session.add(newGame)
    db.session.commit()

    return game_schema.jsonify(newGame)


@app.route('/game', methods=['GET'])
def getGames():
    allGames = Game.query.all()
    result = games_schema.dump(allGames)
    return jsonify(result)


@app.route('/game/<id>', methods=['GET'])
def getGame(id):
    game = Game.query.get(id)
    return game_schema.jsonify(game)


@app.route('/game/<id>', methods=['PUT'])
def updateGame(id):
    if Game.query.get(id):

        game = Game.query.get(id)

        name = request.json['name']
        artwork = request.json['artwork']
        gif = request.json['gif']
        status = request.json['status']

        game.name = name
        game.artwork = artwork
        game.gif = gif
        game.status = status

        db.session.commit()

        return game_schema.jsonify(game)
    else:
        abort(400)
        return jsonify({'message': 'Game Not Found'})

# Delete One Game


@app.route('/game/<id>', methods=['DELETE'])
def deleteGame(id):
    game = Game.query.get(id)
    db.session.delete(game)
    db.session.commit()
    return game_schema.jsonify(game)


@app.route('/challenge/<id>', methods=['POST'])
def createChallenge(id):
    if Game.query.get(id):

        acceptedTypes = ['meme', 'tough', 'troll']

        if request.json['type'] not in acceptedTypes:
            return jsonify({'message': 'Not acceptable challenge Type (lowerCase)'})

        contents = request.json['contents']
        type = request.json['type']
        game_id = id

        newChallenge = Challenge(contents, type, game_id)

        db.session.add(newChallenge)
        db.session.commit()

        return challenge_schema.jsonify(newChallenge)
    else:
        return jsonify({'message': 'No Game Found'})


@app.route('/challenge/<id>', methods=['GET'])
def getChallenges(id):
    if Game.query.get(id):
        getChallenges = Challenge.query.filter_by(game_id=id)
        results = challenges_schema.jsonify(getChallenges)
        return results
    else:
        return jsonify({'message': 'No Game Found'})


@app.route('/challenge/<id>', methods=['PUT'])
def updateChallenge(id):
    if Challenge.query.get(id):
        foundChallenge = Challenge.query.get(id)
        acceptedTypes = ['meme', 'tough', 'troll']

        if request.json['type'] not in acceptedTypes:
            return jsonify({'message': 'Not acceptable challenge Type (lowerCase)'})

        contents = request.json['contents']
        type = request.json['type']

        foundChallenge.contents = contents
        foundChallenge.type = type

        db.session.commit()

        return challenge_schema.jsonify(foundChallenge)

    else:
        return jsonify({'message': 'No Challenge Found'})


if __name__ == '__main__':
    app.run()
