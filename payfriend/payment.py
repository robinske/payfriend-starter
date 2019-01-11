import uuid
from authy.api import AuthyApiClient
from flask import (
    abort,
    Blueprint,
    flash,
    jsonify,
    g,
    render_template,
    redirect,
    request,
    session,
    url_for
)
from flask import current_app as app
from . import utils
from payfriend import db
from payfriend.decorators import (
    display_flash_messages,
    login_required, 
    verification_required,
    verify_authy_request
)
from payfriend.forms import PaymentForm
from payfriend.models import Payment, User


bp = Blueprint('payments', __name__, url_prefix='/payments')


@bp.before_app_request
def load_logged_in_user():
    """
    If a user id is stored in the session, load the user object from
    the database into ``g.user``.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None


def get_user_payments(email):
    user_payments = db.session.query(Payment, User) \
        .join(User) \
        .filter((User.email == email)) \
        .all()

    payments = []
    for (payment, user) in user_payments:
        payments.append({
            "email": user.email,
            "id": payment.id,
            "send_to": payment.send_to,
            "amount": payment.amount,
            "status": payment.status
        })
    
    return payments


@bp.route('/send', methods=["GET", "POST"])
@login_required
@verification_required
@display_flash_messages
def send():
    form = PaymentForm(request.form)
    if form.validate_on_submit():
        send_to = form.send_to.data
        amount = form.amount.data
        authy_id = g.user.authy_id

        # create a unique ID we can use to track payment status
        payment_id = str(uuid.uuid4())

        payment = Payment(payment_id, authy_id, send_to, amount)
        db.session.add(payment)
        db.session.commit()
        return jsonify({ 'success': True })
    
    return render_template("payments/send.html", form=form)


@bp.route('/', methods=["GET", "POST"])
@login_required
@display_flash_messages
def list_payments():
    payments = get_user_payments(g.user.email)
    return render_template('payments/list.html', payments=payments)
