from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


# Create Flask Application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:aizen@localhost:3306/lex'
db = SQLAlchemy(app)

# Reflect Database Tables into Models
metadata = MetaData()

with app.app_context():
    metadata.reflect(bind=db.engine)
    for tablename in metadata.tables:
        table = metadata.tables[tablename]
        globals()[str(tablename)] = type(str(tablename), (db.Model,), {
            '__table__': table
        })
        print(f"Table name: {tablename}")
        for column in table.c:
            print(f"Column: {column.name}")
        print("\n") 

if __name__ == '__main__':
    app.run(debug=True)
