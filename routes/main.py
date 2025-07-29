from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from forms import SearchForm, QuickAddForm, CategoryForm
from models import User, Category, Page, ContentBlock
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing all categories"""
    search_form = SearchForm()
    quick_add_form = QuickAddForm()
    
    # Get user's categories
    categories = Category.query.filter_by(
        user_id=current_user.id, 
        is_deleted=False
    ).order_by(Category.updated_at.desc()).all()
    
    # Get recent pages
    recent_pages = Page.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).order_by(Page.updated_at.desc()).limit(5).all()
    
    # Populate quick add form choices
    quick_add_form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    
    return render_template('main/dashboard.html', 
                         categories=categories, 
                         recent_pages=recent_pages,
                         search_form=search_form,
                         quick_add_form=quick_add_form,
                         title='Dashboard')

@main_bp.route('/search')
@login_required
def search():
    """Search pages and content"""
    query = request.args.get('query', '').strip()
    results = []
    
    if query:
        # Search in page titles and content
        page_results = Page.query.filter(
            and_(
                Page.user_id == current_user.id,
                Page.is_deleted == False,
                or_(
                    Page.title.contains(query),
                    Page.id.in_(
                        db.session.query(ContentBlock.page_id)
                        .filter(ContentBlock.content.contains(query))
                    )
                )
            )
        ).order_by(Page.updated_at.desc()).all()
        
        # Search in categories
        category_results = Category.query.filter(
            and_(
                Category.user_id == current_user.id,
                Category.is_deleted == False,
                or_(
                    Category.title.contains(query),
                    Category.description.contains(query)
                )
            )
        ).order_by(Category.updated_at.desc()).all()
        
        results = {
            'pages': page_results,
            'categories': category_results,
            'query': query
        }
    
    search_form = SearchForm()
    search_form.query.data = query
    
    return render_template('main/search.html', 
                         results=results, 
                         search_form=search_form,
                         title=f'Search: {query}' if query else 'Search')

@main_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    """Toggle between light and dark theme"""
    current_theme = session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    session['theme'] = new_theme
    return jsonify({'theme': new_theme})

@main_bp.route('/trash')
@login_required
def trash():
    """View deleted categories and pages"""
    deleted_categories = Category.query.filter_by(
        user_id=current_user.id,
        is_deleted=True
    ).order_by(Category.deleted_at.desc()).all()
    
    deleted_pages = Page.query.filter_by(
        user_id=current_user.id,
        is_deleted=True
    ).order_by(Page.deleted_at.desc()).all()
    
    return render_template('main/trash.html',
                         deleted_categories=deleted_categories,
                         deleted_pages=deleted_pages,
                         title='Trash')

@main_bp.route('/quick-add-page', methods=['POST'])
@login_required
def quick_add_page():
    """Quick add a new page"""
    form = QuickAddForm()
    
    # Populate choices
    categories = Category.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    form.category_id.choices = [(cat.id, cat.title) for cat in categories]
    
    if form.validate_on_submit():
        category = Category.query.filter_by(
            id=form.category_id.data,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if category:
            page = Page(
                title=form.title.data,
                category_id=category.id,
                user_id=current_user.id
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
        else:
            flash('Invalid category selected.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/restore/<item_type>/<int:item_id>', methods=['POST'])
@login_required
def restore_item(item_type, item_id):
    """Restore item from trash"""
    if item_type == 'category':
        item = Category.query.filter_by(id=item_id, user_id=current_user.id).first()
    elif item_type == 'page':
        item = Page.query.filter_by(id=item_id, user_id=current_user.id).first()
    else:
        flash('Invalid item type.', 'danger')
        return redirect(url_for('main.trash'))
    
    if item and item.is_deleted:
        item.restore()
        db.session.commit()
        flash(f'{item_type.title()} restored successfully!', 'success')
    else:
        flash('Item not found or not deleted.', 'danger')
    
    return redirect(url_for('main.trash'))

@main_bp.route('/permanent-delete/<item_type>/<int:item_id>', methods=['POST'])
@login_required
def permanent_delete(item_type, item_id):
    """Permanently delete item"""
    if item_type == 'category':
        item = Category.query.filter_by(id=item_id, user_id=current_user.id).first()
    elif item_type == 'page':
        item = Page.query.filter_by(id=item_id, user_id=current_user.id).first()
    else:
        flash('Invalid item type.', 'danger')
        return redirect(url_for('main.trash'))
    
    if item and item.is_deleted:
        db.session.delete(item)
        db.session.commit()
        flash(f'{item_type.title()} permanently deleted!', 'success')
    else:
        flash('Item not found or not deleted.', 'danger')
    
    return redirect(url_for('main.trash'))