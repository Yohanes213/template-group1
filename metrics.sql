CREATE TABLE IF NOT EXISTS "backtest_metrics"(
    "id" SERIAL PRIMARY KEY NOT NULL,
    "sharpe_ratio" float,
    "total_return" float,
    "average_return" float,
    "total_drawdown" float,
    "total_duration" int
);

CREATE TABLE IF NOT EXISTS "scene"(
    "id" SERIAL PRIMARY KEY NOT NULL,
    "strategy" VARCHAR(255),
    "start_Date" VARCHAR(255),
    "end_date" VARCHAR(255)
)