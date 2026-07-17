# -*- coding: utf-8 -*-
"""Functional tests for the admin blog authoring views."""
from myflaskapp.models.post import Post
from .factories import UserFactory


def _login(testapp, user, password='myprecious'):
    res = testapp.get("/")
    form = res.forms['loginForm']
    form['username'] = user.username
    form['password'] = password
    return form.submit().follow()


def _enable_csrf(app):
    app.config['WTF_CSRF_ENABLED'] = True


class TestNewBlog:

    def test_valid_csrf_submission_creates_post(self, app, db, testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()
        _login(testapp, admin)
        _enable_csrf(app)

        res = testapp.get('/new_blog')
        form = res.forms['new_post_form']
        assert form['csrf_token'].value
        form['title'] = 'Created title'
        form['slug'] = 'created-slug'
        form['content'] = 'created body'
        form.submit()

        post = Post.query.one()
        assert post.title == 'Created title'
        assert post.slug == 'created-slug'
        assert post.body == 'created body'
        assert post.user_id == admin.id

    def test_missing_or_invalid_csrf_does_not_create_post(self, app, db,
                                                          testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()
        _login(testapp, admin)
        _enable_csrf(app)

        data = {'title': 'Forged', 'slug': 'forged', 'content': 'forged'}
        testapp.post('/new_blog', data)
        invalid_data = dict(data, csrf_token='invalid-token')
        testapp.post('/new_blog', invalid_data)

        assert Post.query.count() == 0

    def test_non_admin_cannot_create_post(self, app, db, testapp):
        user = UserFactory(password='myprecious', is_admin=False)
        db.session.commit()
        _login(testapp, user)
        _enable_csrf(app)

        res = testapp.post('/new_blog', {
            'title': 'Forbidden',
            'slug': 'forbidden',
            'content': 'forbidden',
        })

        assert res.status_code == 200
        assert Post.query.count() == 0


class TestEditBlog:

    def test_edit_updates_existing_post_in_place(self, app, db, testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()

        post = Post(title='Original', slug='orig-slug', body='original body')
        post.save()
        admin.posts.append(post)
        admin.save()
        post_id = post.id

        _login(testapp, admin)
        _enable_csrf(app)

        old_count = len(Post.query.all())
        res = testapp.get('/edit_blog/{0}/'.format(post_id))
        form = res.forms['new_post_form']
        assert form['csrf_token'].value
        form['title'] = 'Updated title'
        form['slug'] = 'updated-slug'
        form['content'] = 'updated body'
        form.submit()

        # No duplicate created.
        assert len(Post.query.all()) == old_count
        # Existing record updated in place.
        updated = Post.query.filter_by(id=post_id).first()
        assert updated.title == 'Updated title'
        assert updated.slug == 'updated-slug'
        assert updated.body == 'updated body'

    def test_missing_or_invalid_csrf_does_not_modify_post(self, app, db,
                                                          testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()
        post = Post(title='Original', slug='orig-slug', body='original body')
        post.save()
        admin.posts.append(post)
        admin.save()
        _login(testapp, admin)
        _enable_csrf(app)

        url = '/edit_blog/{0}/'.format(post.id)
        data = {'title': 'Forged', 'slug': 'forged', 'content': 'forged'}
        testapp.post(url, data)
        invalid_data = dict(data, csrf_token='invalid-token')
        testapp.post(url, invalid_data)

        db.session.refresh(post)
        assert post.title == 'Original'
        assert post.slug == 'orig-slug'
        assert post.body == 'original body'

    def test_non_admin_cannot_edit_post(self, app, db, testapp):
        user = UserFactory(password='myprecious', is_admin=False)
        db.session.commit()
        post = Post(title='Original', slug='orig-slug', body='original body')
        post.save()
        _login(testapp, user)
        _enable_csrf(app)

        testapp.post('/edit_blog/{0}/'.format(post.id), {
            'title': 'Forbidden',
            'slug': 'forbidden',
            'content': 'forbidden',
        })

        db.session.refresh(post)
        assert post.title == 'Original'
        assert post.slug == 'orig-slug'
        assert post.body == 'original body'

    def test_edit_missing_post_returns_404(self, db, testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()

        _login(testapp, admin)

        res = testapp.get('/edit_blog/999999/', expect_errors=True)
        assert res.status_code == 404
