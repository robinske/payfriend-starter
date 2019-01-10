from flask import render_template


def unauthorized(e):
    return render_template('error.html', message='401 unauthorized'), 401


def forbidden(e):
    return render_template('error.html', message='403 forbidden'), 403


def page_not_found(e):
    return render_template('error.html', message='404 not found'), 404


def internal_error(e):
    return render_template('error.html', message='500 internal error'), 500
