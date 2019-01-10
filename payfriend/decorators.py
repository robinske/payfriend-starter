from flask import abort, flash, g, redirect, request, session, url_for
from functools import wraps
from . import utils


def login_required(view):
    """
    View decorator that redirects anonymous users to the login page.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def verification_required(view):
    """
    View decorator that redirects unverified users to the verification page.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user and not g.user.authy_id:
            flash("Please verify your phone number before continuing.")
            (country_code, phone) = utils.parse_phone_number(g.user.phone_number)
            utils.start_verification(country_code, phone)
            return redirect(url_for('auth.verify'))

        return view(**kwargs)

    return wrapped_view


def display_flash_messages(f):
    """
    Displays messages sent from Javascript.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        message = request.form.get("flash_message")
        if request.method == 'POST' and  message:
            flash(message)
        
        return f(*args, **kwargs)
    return decorated_function


def verify_authy_request(f):
    """
    Verifies that a OneTouch callback request came from Authy
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the request URL without the parameters
        client = utils.get_authy_client()

        response = client.one_touch.validate_one_touch_signature(
            request.headers['X-Authy-Signature'],
            request.headers['X-Authy-Signature-Nonce'],
            request.method,
            request.url,
            request.json
        )
        if response:
            # The two signatures match - this request is authentic
            return f(*args, **kwargs)

        # The signatures didn't match - abort this request
        return abort(400)
    return decorated_function