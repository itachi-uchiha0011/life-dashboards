import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from models import Page, ContentBlock, FileUpload
from app import db

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'md'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename):
    """Check if file is an image"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@api_bp.route('/content-blocks', methods=['POST'])
@login_required
def create_content_block():
    """Create or update content block"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    page_id = data.get('page_id')
    block_id = data.get('block_id')
    block_type = data.get('block_type', 'text')
    content = data.get('content', '')
    metadata = data.get('metadata', {})
    order = data.get('order', 0)
    
    # Verify page ownership
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    try:
        if block_id:
            # Update existing block
            block = ContentBlock.query.filter_by(
                block_id=block_id,
                page_id=page_id
            ).first()
            
            if block:
                block.block_type = block_type
                block.content = content
                block.metadata = metadata
                block.order = order
            else:
                return jsonify({'error': 'Block not found'}), 404
        else:
            # Create new block
            block = ContentBlock(
                block_id=str(uuid.uuid4()),
                page_id=page_id,
                block_type=block_type,
                content=content,
                metadata=metadata,
                order=order
            )
            db.session.add(block)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'block': {
                'id': block.id,
                'block_id': block.block_id,
                'block_type': block.block_type,
                'content': block.content,
                'metadata': block.metadata,
                'order': block.order,
                'created_at': block.created_at.isoformat(),
                'updated_at': block.updated_at.isoformat()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save content block'}), 500

@api_bp.route('/content-blocks/<block_id>', methods=['DELETE'])
@login_required
def delete_content_block(block_id):
    """Delete content block"""
    block = ContentBlock.query.filter_by(block_id=block_id).first()
    
    if not block:
        return jsonify({'error': 'Block not found'}), 404
    
    # Verify page ownership
    page = Page.query.filter_by(
        id=block.page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    try:
        db.session.delete(block)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete content block'}), 500

@api_bp.route('/content-blocks/reorder', methods=['POST'])
@login_required
def reorder_content_blocks():
    """Reorder content blocks"""
    data = request.get_json()
    
    if not data or 'blocks' not in data:
        return jsonify({'error': 'No blocks data provided'}), 400
    
    page_id = data.get('page_id')
    blocks = data.get('blocks')
    
    # Verify page ownership
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    try:
        for item in blocks:
            block_id = item.get('block_id')
            order = item.get('order')
            
            block = ContentBlock.query.filter_by(
                block_id=block_id,
                page_id=page_id
            ).first()
            
            if block:
                block.order = order
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reorder blocks'}), 500

@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload file to page"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    page_id = request.form.get('page_id')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not page_id:
        return jsonify({'error': 'No page ID provided'}), 400
    
    # Verify page ownership
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Create upload path
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        
        try:
            # Save file
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create database record
            file_upload = FileUpload(
                original_filename=original_filename,
                filename=unique_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type,
                is_image=is_image_file(original_filename),
                page_id=page_id,
                user_id=current_user.id
            )
            
            db.session.add(file_upload)
            db.session.commit()
            
            # Generate URL for file access
            file_url = url_for('static', filename=f'uploads/{current_user.id}/{unique_filename}')
            
            return jsonify({
                'success': True,
                'file': {
                    'id': file_upload.id,
                    'original_filename': file_upload.original_filename,
                    'filename': file_upload.filename,
                    'file_size': file_upload.file_size,
                    'mime_type': file_upload.mime_type,
                    'is_image': file_upload.is_image,
                    'url': file_url,
                    'created_at': file_upload.created_at.isoformat()
                }
            })
        
        except Exception as e:
            # Clean up file if database save fails
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.rollback()
            return jsonify({'error': 'Failed to upload file'}), 500
    
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@api_bp.route('/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete uploaded file"""
    file_upload = FileUpload.query.filter_by(
        id=file_id,
        user_id=current_user.id
    ).first()
    
    if not file_upload:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Delete physical file
        if os.path.exists(file_upload.file_path):
            os.remove(file_upload.file_path)
        
        # Delete database record
        db.session.delete(file_upload)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete file'}), 500

@api_bp.route('/page/<int:page_id>/content', methods=['GET'])
@login_required
def get_page_content(page_id):
    """Get all content blocks for a page"""
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    blocks = ContentBlock.query.filter_by(
        page_id=page_id
    ).order_by(ContentBlock.order.asc()).all()
    
    files = FileUpload.query.filter_by(
        page_id=page_id
    ).order_by(FileUpload.created_at.desc()).all()
    
    content_blocks = []
    for block in blocks:
        content_blocks.append({
            'id': block.id,
            'block_id': block.block_id,
            'block_type': block.block_type,
            'content': block.content,
            'metadata': block.metadata,
            'order': block.order,
            'created_at': block.created_at.isoformat(),
            'updated_at': block.updated_at.isoformat()
        })
    
    file_uploads = []
    for file in files:
        file_url = url_for('static', filename=f'uploads/{current_user.id}/{file.filename}')
        file_uploads.append({
            'id': file.id,
            'original_filename': file.original_filename,
            'filename': file.filename,
            'file_size': file.file_size,
            'mime_type': file.mime_type,
            'is_image': file.is_image,
            'url': file_url,
            'created_at': file.created_at.isoformat()
        })
    
    return jsonify({
        'success': True,
        'content_blocks': content_blocks,
        'files': file_uploads
    })

@api_bp.route('/autosave', methods=['POST'])
@login_required
def autosave():
    """Autosave page content"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    page_id = data.get('page_id')
    content_blocks = data.get('content_blocks', [])
    
    # Verify page ownership
    page = Page.query.filter_by(
        id=page_id,
        user_id=current_user.id,
        is_deleted=False
    ).first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    try:
        # Update or create content blocks
        for block_data in content_blocks:
            block_id = block_data.get('block_id')
            
            if block_id:
                block = ContentBlock.query.filter_by(
                    block_id=block_id,
                    page_id=page_id
                ).first()
                
                if block:
                    block.content = block_data.get('content', '')
                    block.metadata = block_data.get('metadata', {})
                    block.order = block_data.get('order', 0)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Content saved'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save content'}), 500