from system import app, db
from flask_migrate import Migrate


migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
