import phonenumbers
from authy.api import AuthyApiClient
from flask import current_app as app
from flask import flash, g, request, session


def parse_phone_number(full_phone):
    """
    Parses the phone number from E.164 format

    :param full_phone: phone number in E.164 format
    :returns: tuple (country_code, phone)
    """
    pn = phonenumbers.parse(full_phone)
    return (pn.country_code, pn.national_number)


def get_authy_client():
    return AuthyApiClient(app.config['AUTHY_API_KEY'])


def start_verification(country_code, phone, channel='sms'):
    """
    Sends a verification code to the user's phone number 
    via the specified channel

    :param country_code: country code for the phone number
    :param phone: national format phone number
    :param channel: either 'sms' or 'call'
    """
    api = get_authy_client()
    try: 
        verification = api.phones.verification_start(
            phone, country_code, via=channel)
        if verification.ok():
            flash(verification.content['message'])
        else:
            flash(verification.errors()['message'])
    except Exception as e:
        flash("Error sending code: {}".format(e))


def check_verification(country_code, phone, code):
    """
    Validates a verification code

    :param country_code: country code for the phone number
    :param phone: national format phone number
    :param code: verification code from user input
    """
    api = get_authy_client()
    try:
        verification = api.phones.verification_check(
            phone, country_code, code)
        if verification.ok():
            flash(verification.content['message'])
            return True
        else:
            flash(verification.errors()['message'])
    except Exception as e:
        flash("Error validating code: {}".format(e))
    
    return False


def create_authy_user(email, country_code, phone):
    """
    Creates a user with the Authy API

    :param email: email to be associated with the user. 
        Used by the API for account recovery
    :param country_code: country code for the phone number
    :param phone: national format phone number
    :returns: the generated Authy ID
    """
    api = get_authy_client()
    authy_user = api.users.create(email, phone, country_code)
    if authy_user.ok():
        return authy_user.id
    else:
        flash("Error creating Authy user: {}".format(authy_user.errors()))
        return None
