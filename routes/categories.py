from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from forms import CategoryForm, PageForm
from models import Category, Page
from app.extensions import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create a new category"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            title=form.title.data,
            description=form.description.data,
            icon=form.icon.data or '📁',
            color=form.color.data or '#6366f1',
            user_id=current_user.id
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{category.title}" created successfully!', 'success')
            return redirect(url_for('categories.view_category', category_slug=category.slug))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create category. Please try again.', 'danger')
    
    return render_template('categories/create.html', form=form, title='New Category')

@categories_bp.route('/<category_slug>')
@login_required
def view_category(category_slug):
    """View category and its pages"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    # Get pages in this category (excluding nested pages)
    pages = Page.query.filter_by(
        category_id=category.id,
        user_id=current_user.id,
        is_deleted=False,
        parent_id=None
    ).order_by(Page.updated_at.desc()).all()
    
    return render_template('categories/view.html', 
                         category=category, 
                         pages=pages,
                         title=category.title)

@categories_bp.route('/<category_slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_slug):
    """Edit category"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        # Check if title changed and generate new slug if needed
        if form.title.data != category.title:
            category.title = form.title.data
            category.slug = category.generate_unique_slug(form.title.data)
        
        category.description = form.description.data
        category.icon = form.icon.data or '📁'
        category.color = form.color.data or '#6366f1'
        
        try:
            db.session.commit()
            flash(f'Category "{category.title}" updated successfully!', 'success')
            return redirect(url_for('categories.view_category', category_slug=category.slug))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update category. Please try again.', 'danger')
    
    return render_template('categories/edit.html', 
                         form=form, 
                         category=category, 
                         title=f'Edit {category.title}')

@categories_bp.route('/<category_slug>/delete', methods=['POST'])
@login_required
def delete_category(category_slug):
    """Soft delete category"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    category.soft_delete()
    db.session.commit()
    
    flash(f'Category "{category.title}" moved to trash.', 'info')
    return redirect(url_for('main.dashboard'))

@categories_bp.route('/<category_slug>/new-page', methods=['GET', 'POST'])
@login_required
def create_page(category_slug):
    """Create a new page in category"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    form = PageForm()
    
    # Set category choices
    form.category_id.choices = [(category.id, category.title)]
    form.category_id.data = category.id
    
    # Set parent page choices (pages in this category)
    pages_in_category = Page.query.filter_by(
        category_id=category.id,
        user_id=current_user.id,
        is_deleted=False
    ).all()
    form.parent_id.choices = [('', 'None')] + [(p.id, p.title) for p in pages_in_category]
    
    if form.validate_on_submit():
        page = Page(
            title=form.title.data,
            icon=form.icon.data or '📄',
            category_id=category.id,
            user_id=current_user.id,
            parent_id=form.parent_id.data if form.parent_id.data else None,
            is_template=bool(form.template_type.data),
            template_type=form.template_type.data if form.template_type.data else None
        )
        
        try:
            db.session.add(page)
            db.session.commit()
            flash(f'Page "{page.title}" created successfully!', 'success')
            return redirect(url_for('categories.view_page', 
                                  category_slug=category.slug, 
                                  page_slug=page.slug))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create page. Please try again.', 'danger')
    
    return render_template('pages/create.html', 
                         form=form, 
                         category=category, 
                         title=f'New Page in {category.title}')

@categories_bp.route('/<category_slug>/<page_slug>')
@login_required
def view_page(category_slug, page_slug):
    """View a specific page"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    page = Page.query.filter_by(
        slug=page_slug,
        category_id=category.id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    # Get child pages if any
    child_pages = Page.query.filter_by(
        parent_id=page.id,
        user_id=current_user.id,
        is_deleted=False
    ).order_by(Page.created_at.asc()).all()
    
    return render_template('pages/view.html', 
                         category=category, 
                         page=page,
                         child_pages=child_pages,
                         title=page.title)

@categories_bp.route('/<category_slug>/<page_slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(category_slug, page_slug):
    """Edit a page"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    page = Page.query.filter_by(
        slug=page_slug,
        category_id=category.id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    form = PageForm(obj=page)
    
    # Set category choices
    user_categories = Category.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    form.category_id.choices = [(cat.id, cat.title) for cat in user_categories]
    
    # Set parent page choices (excluding self and children)
    available_parents = Page.query.filter_by(
        category_id=form.category_id.data or category.id,
        user_id=current_user.id,
        is_deleted=False
    ).filter(Page.id != page.id).all()
    
    form.parent_id.choices = [('', 'None')] + [(p.id, p.title) for p in available_parents]
    
    if form.validate_on_submit():
        # Check if title changed and generate new slug if needed
        if form.title.data != page.title:
            page.title = form.title.data
            page.slug = page.generate_unique_slug(form.title.data)
        
        page.icon = form.icon.data or '📄'
        page.category_id = form.category_id.data
        page.parent_id = form.parent_id.data if form.parent_id.data else None
        page.is_template = bool(form.template_type.data)
        page.template_type = form.template_type.data if form.template_type.data else None
        
        try:
            db.session.commit()
            
            # If category changed, redirect to new category
            if page.category_id != category.id:
                new_category = Category.query.get(page.category_id)
                flash(f'Page "{page.title}" updated successfully!', 'success')
                return redirect(url_for('categories.view_page', 
                                      category_slug=new_category.slug, 
                                      page_slug=page.slug))
            else:
                flash(f'Page "{page.title}" updated successfully!', 'success')
                return redirect(url_for('categories.view_page', 
                                      category_slug=category.slug, 
                                      page_slug=page.slug))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update page. Please try again.', 'danger')
    
    return render_template('pages/edit.html', 
                         form=form, 
                         category=category, 
                         page=page,
                         title=f'Edit {page.title}')

@categories_bp.route('/<category_slug>/<page_slug>/delete', methods=['POST'])
@login_required
def delete_page(category_slug, page_slug):
    """Soft delete page"""
    category = Category.query.filter_by(
        slug=category_slug,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    page = Page.query.filter_by(
        slug=page_slug,
        category_id=category.id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    page.soft_delete()
    db.session.commit()
    
    flash(f'Page "{page.title}" moved to trash.', 'info')
    return redirect(url_for('categories.view_category', category_slug=category.slug))