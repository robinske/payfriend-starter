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


def update_payment_status(payment, status):
    # once a payment status has been set, don't allow that to change
    # this requires a new transaction in order to be PSD2 compliant
    if payment.status != 'pending':
        flash("Error: payment request was already {}. Please start a new transaction.".format(
            payment.status))
        return redirect(url_for('payments.list_payments'))

    payment.status = status
    db.session.commit()


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


@bp.route('/callback', methods=["POST"])
@verify_authy_request
def callback():
    """
    Used by Twilio to send a notification when the user 
    approves or denies a push authorization in the Authy app
    """
    push_id = request.json.get('uuid')
    status = request.json.get('status')
    payment = Payment.query.filter_by(push_id=push_id).first()

    update_payment_status(payment, status)
    return ('', 200)


@bp.route('/status', methods=["GET", "POST"])
@login_required
def status():
    """
    Used by AJAX requests to check the OneTouch verification status of a payment
    """
    payment_id = request.args.get('payment_id')
    payment = Payment.query.get(payment_id)
    return payment.status


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

        (push_id, errors) = utils.send_push_auth(authy_id, send_to, amount)
        if push_id:
            payment = Payment(payment_id, authy_id, send_to, amount, push_id)
            db.session.add(payment)
            db.session.commit()
            return jsonify({
                "success": True,
                "payment_id": payment_id
            })
        else:
            flash("Error sending authorization. {}".format(errors))
            return jsonify({"success": False})
    
    return render_template("payments/send.html", form=form)


@bp.route('/', methods=["GET", "POST"])
@login_required
@display_flash_messages
def list_payments():
    payments = get_user_payments(g.user.email)
    return render_template('payments/list.html', payments=payments)


def check_sms_auth(authy_id, payment_id, code):
    """
    Validates an SMS OTP.
    """
    if utils.check_sms_auth(g.user.authy_id, payment_id, code):
        payment = Payment.query.get(payment_id)
        update_payment_status(payment, 'approved')
        return redirect(url_for('payments.list_payments'))
    else:
        abort(400)


@bp.route('/auth/sms', methods=["POST"])
@login_required
def sms_auth():
    if not g.user.authy_id:
        return(redirect(url_for('auth.verify')))

    payment_id = request.form['payment_id']
    session['payment_id'] = payment_id
    payment = Payment.query.get(payment_id)
    
    if utils.send_sms_auth(payment):
        return redirect(url_for('auth.verify'))
    else:
        return redirect(url_for('payments.send'))