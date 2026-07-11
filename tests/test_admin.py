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


class TestEditBlog:

    def test_edit_updates_existing_post_in_place(self, db, testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()

        post = Post(title='Original', slug='orig-slug', body='original body')
        post.save()
        admin.posts.append(post)
        admin.save()
        post_id = post.id

        _login(testapp, admin)

        old_count = len(Post.query.all())
        res = testapp.get('/edit_blog/{0}/'.format(post_id))
        form = res.forms['new_post_form']
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

    def test_edit_missing_post_returns_404(self, db, testapp):
        admin = UserFactory(password='myprecious', is_admin=True)
        db.session.commit()

        _login(testapp, admin)

        res = testapp.get('/edit_blog/999999/', expect_errors=True)
        assert res.status_code == 404
