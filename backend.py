from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaProducer
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234567@localhost:5432/backtest'
db = SQLAlchemy(app)

class Backtest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    strategy = db.Column(db.String(80), nullable=False)
    result = db.Column(db.JSON, nullable=True)

with app.app_context():
    db.create_all()

KAFKA_SERVER = 'localhost:9092'

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@app.route('/process', methods=['POST'])
def backtest():
    data = request.json
    backtest = Backtest(
        start_date=data['Start date'],
        end_date=data['End date'],
        strategy=data['Startegy']
    )

    db.session.add(backtest)
    db.session.commit()

    # Send message to Kafka
    producer.send('scene', {
        'backtest_id': backtest.id,
        'start_date': data['Start date'],
        'end_date': data['End date'],
        'strategy': data['Startegy']
    })
    return jsonify({"message": "Backtest request submitted."}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
