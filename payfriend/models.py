from payfriend import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    Represents a single user in the system.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    phone_number = db.Column(db.String(30), unique=True)
    authy_id = db.Column(db.Integer)

    def __init__(self, email, password, phone_number):
        self.email = email
        self.password = password
        self.phone_number = phone_number

    def __repr__(self):
        return '<User %r>' % self.email

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Payment(db.Model):
    """
    Represents a single payment in the system.
    """
    __tablename__ = 'payments'

    AUTHY_STATUSES = (
        'pending',
        'approved',
        'denied'
    )

    id = db.Column(db.String(128), primary_key=True)
    authy_id = db.Column(db.Integer, db.ForeignKey('users.authy_id'))
    send_to = db.Column(db.String(128))
    amount = db.Column(db.Integer)
    push_id = db.Column(db.String(128))
    status = db.Column(db.Enum(*AUTHY_STATUSES, name='authy_statuses'))

    def __init__(self, id, authy_id, send_to, amount, push_id, 
                 status='pending'):
        self.id = id
        self.authy_id = authy_id
        self.send_to = send_to
        self.amount = amount
        self.push_id = push_id
        self.status = status
    
    def __repr__(self):
        return '<Payment %r>' % self.id