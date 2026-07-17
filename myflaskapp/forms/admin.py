# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextAreaField, TextField


class AdminBlogForm(Form):
    title = TextField('Post Title')
    slug = TextAreaField('Slug')
    content = TextAreaField('Body')
