from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask import current_app as app
from . import utils
from payfriend import db
from payfriend.forms import RegisterForm, LoginForm, VerifyForm
from payfriend.models import User


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    """
    If a user id is stored in the session, load the user object from
    the database into ``g.user``.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    Register a new user.

    Validates that the email is not already taken. Hashes the
    password for security.
    """
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        full_phone = form.full_phone.data
        channel = form.channel.data

        # Authy API requires separate country code
        (country_code, phone) = utils.parse_phone_number(full_phone)

        try:
            utils.start_verification(country_code, phone, channel)
            user = User(email, password, full_phone)
            db.session.add(user)
            db.session.commit()
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('auth.verify'))
        except Exception as e:
            flash('Error sending phone verification. {}'.format(e))

    return render_template('auth/register.html', form=form)


def handle_verified_user(email, country_code, phone, code):
    """
    After user verifies their phone number, create the Authy user
    and update the database with their Authy ID.
    """
    # if verification passes, create the authy user
    authy_id = utils.create_authy_user(email, country_code, phone)

    # update the database with the authy id
    user = User.query.filter_by(email=email).first()
    user.authy_id = authy_id
    db.session.commit()
    return redirect(url_for('payments.send'))


@bp.route('/verify', methods=('GET', 'POST'))
def verify():
    """
    Generic endpoint to verify a code entered by the user.
    """
    form = VerifyForm(request.form)
    validated = form.validate_on_submit()

    if form.validate_on_submit():
        email = g.user.email
        (country_code, phone) = utils.parse_phone_number(g.user.phone_number)
        code = form.verification_code.data

        # route based on the type of verification
        if not g.user.authy_id:
            if utils.check_verification(country_code, phone, code):
                return handle_verified_user(email, country_code, phone, code)
        else:
            payment_id = session['payment_id']
            return check_sms_auth(g.user.authy_id, payment_id, code)
    return render_template('auth/verify.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Log in a registered user by adding the user id to the session.
    """
    form = LoginForm(request.form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        error = None
        user = User.query.filter_by(email=email).first()
        if user is None:
            error = 'Incorrect email.'
        elif not user.verify_password(password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session
            # redirect to payments
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('payments.send'))

        flash(error)

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    """
    Clear the current session, including the stored user id.
    """
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
