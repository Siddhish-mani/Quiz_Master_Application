from app import create_app
from models import db

app = create_app()

def initialize_database():
    with app.app_context():
        db.create_all()
        
        from models import User
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                username='admin',
                email='admin@quizmaster.com',
                full_name='Administrator',
                is_admin=True
            )
            admin.set_password('admin123') 
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")

if __name__ == '__main__':
    initialize_database()
    print("Database initialized successfully")