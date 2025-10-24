from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Page, Category
from app.extensions import db

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/<int:page_id>')
@login_required
def view_page_by_id(page_id):
    """View page by ID (useful for API calls)"""
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    category = page.category
    
    return redirect(url_for('categories.view_page', 
                          category_slug=category.slug, 
                          page_slug=page.slug))

@pages_bp.route('/<int:page_id>/info')
@login_required
def page_info(page_id):
    """Get page information as JSON"""
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    return jsonify({
        'id': page.id,
        'title': page.title,
        'slug': page.slug,
        'icon': page.icon,
        'created_at': page.created_at.isoformat(),
        'updated_at': page.updated_at.isoformat(),
        'category': {
            'id': page.category.id,
            'title': page.category.title,
            'slug': page.category.slug
        },
        'parent_id': page.parent_id,
        'is_template': page.is_template,
        'template_type': page.template_type,
        'content_blocks_count': len(page.content_blocks),
        'child_pages_count': len(page.children)
    })