from __future__ import (absolute_import, division, print_function, unicode_literals)
from backtrader.analyzers import Returns, DrawDown, SharpeRatio, TradeAnalyzer

import backtrader as bt
import datetime
import os.path
import sys
import json
from kafka import KafkaProducer

KAFKA_TOPIC = 'Backtesting_exm'
KAFKA_SERVER = 'localhost:9092'

values = {"Startegy": "BTC", "Start date": "2023-06-18", "End date": "2024-06-18"}

# Send metrics to Kafka
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
producer.send(KAFKA_TOPIC, json.dumps(values).encode('utf-8'))
producer.flush()  # Ensure all messages are sent
