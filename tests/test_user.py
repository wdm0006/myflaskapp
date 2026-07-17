# -*- coding: utf-8 -*-
"""Functional tests for the user account views."""
from flask import url_for

from myflaskapp.models.user import User
from .factories import UserFactory


def _login(testapp, user, password='myprecious'):
    res = testapp.get("/")
    form = res.forms['loginForm']
    form['username'] = user.username
    form['password'] = password
    return form.submit().follow()


def _reload(user_id):
    return User.query.filter_by(id=user_id).first()


class TestUnsubscribe:

    def test_confirm_rejects_get(self, db, testapp):
        user = UserFactory(password='myprecious')
        db.session.commit()
        user_id, username = user.id, user.username

        _login(testapp, user)

        res = testapp.get(url_for('user.unsubscribe_confirm'), expect_errors=True)
        assert res.status_code == 405

        # The account is untouched by the GET.
        unchanged = _reload(user_id)
        assert unchanged.username == username
        assert unchanged.active is True

    def test_confirmation_page_posts_the_form(self, db, testapp):
        user = UserFactory(password='myprecious')
        db.session.commit()

        _login(testapp, user)

        res = testapp.get(url_for('user.unsubscribe'))
        form = res.forms['unsubscribeForm']
        assert form.method.upper() == 'POST'

    def test_valid_post_unsubscribes_and_logs_out(self, db, testapp):
        user = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()
        user_id, username, email = user.id, user.username, user.email

        res = _login(testapp, user)
        assert 'Logged in as %s' % (username,) in res

        res = testapp.get(url_for('user.unsubscribe'))
        res.forms['unsubscribeForm'].submit().follow()

        unsubscribed = _reload(user_id)
        assert unsubscribed.username == '%s (Unsubscribed)' % (username,)
        assert unsubscribed.email == '%s (Unsubscribed)' % (email,)
        assert unsubscribed.is_admin is False
        assert unsubscribed.active is False

        # The session is gone: the navbar offers the login form again.
        res = testapp.get(url_for('public.home'))
        assert 'Logged in as' not in res
        assert 'loginForm' in res

    def test_valid_post_carries_a_csrf_token(self, app, db, testapp):
        user = UserFactory(password='myprecious')
        db.session.commit()
        user_id, username = user.id, user.username

        _login(testapp, user)
        app.config['WTF_CSRF_ENABLED'] = True

        res = testapp.get(url_for('user.unsubscribe'))
        form = res.forms['unsubscribeForm']
        assert form['csrf_token'].value

        form.submit().follow()

        unsubscribed = _reload(user_id)
        assert unsubscribed.username == '%s (Unsubscribed)' % (username,)
        assert unsubscribed.active is False

    def test_post_without_csrf_token_does_not_unsubscribe(self, app, db, testapp):
        user = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()
        user_id, username = user.id, user.username

        _login(testapp, user)
        app.config['WTF_CSRF_ENABLED'] = True

        testapp.post(url_for('user.unsubscribe_confirm'), {})

        unchanged = _reload(user_id)
        assert unchanged.username == username
        assert unchanged.is_admin is True
        assert unchanged.active is True

    def test_post_with_invalid_csrf_token_does_not_unsubscribe(self, app, db, testapp):
        user = UserFactory(password='myprecious')
        db.session.commit()
        user_id, username = user.id, user.username

        _login(testapp, user)
        app.config['WTF_CSRF_ENABLED'] = True

        testapp.post(url_for('user.unsubscribe_confirm'), {'csrf_token': 'not-a-real-token'})

        unchanged = _reload(user_id)
        assert unchanged.username == username
        assert unchanged.active is True
