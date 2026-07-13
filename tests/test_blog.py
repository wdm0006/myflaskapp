# -*- coding: utf-8 -*-
"""Functional tests for the public blog views."""
from myflaskapp.models.post import Post
from .factories import UserFactory


class TestBlogDetail:

    def test_existing_post_renders(self, db, testapp):
        author = UserFactory(password='myprecious')
        db.session.commit()

        post = Post(title='A title', slug='a-slug', body='some body')
        post.save()
        author.posts.append(post)
        author.save()

        res = testapp.get('/post_detail/{0}/'.format(post.id))
        assert res.status_code == 200
        assert 'A title' in res

    def test_missing_post_returns_404(self, db, testapp):
        res = testapp.get('/post_detail/999999/', expect_errors=True)
        assert res.status_code == 404
