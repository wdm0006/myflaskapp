# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, abort, request

from flask_login import login_required, current_user
from myflaskapp.forms.admin import AdminBlogForm
from myflaskapp.models.post import Post
from myflaskapp.utils import render_extensions

blueprint = Blueprint('admin', __name__, static_folder="../static")


@blueprint.route("/new_blog", methods=["GET", "POST"])
@login_required
def new_blog():
    if not current_user.is_admin:
        return render_extensions('401.html')

    form = AdminBlogForm(request.form)
    if form.validate_on_submit():
        post = Post(title=form.title.data or '', body=form.content.data or '',
                    slug=form.slug.data or '')
        post.save()

        current_user.posts.append(post)
        current_user.save()

    return render_extensions('admin/new_blog.html', form=form)

@blueprint.route("/edit_blog/<blog_id>/", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id):
    if not current_user.is_admin:
        return render_extensions('401.html')

    post_obj = Post.query.filter_by(id=int(blog_id)).first()
    if post_obj is None:
        abort(404)

    form = AdminBlogForm(request.form)
    if form.validate_on_submit():
        post_obj.title = form.title.data or ''
        post_obj.slug = form.slug.data or ''
        post_obj.body = form.content.data or ''
        post_obj.save()

    post_content = {
        'title': str(post_obj.title),
        'slug': str(post_obj.slug),
        'body': str(post_obj.body),
    }

    return render_extensions('admin/edit_blog.html', post=post_content,
                             form=form)
