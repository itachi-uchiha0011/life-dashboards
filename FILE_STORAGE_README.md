# File Storage Configuration

This application now supports both local and cloud storage for files with the following features:

## Features Added

1. **Open in Browser**: Users can now view files directly in the browser without downloading
2. **Cloudinary Integration**: Production environment uses Cloudinary for file storage
3. **Local Development**: Development environment uses local file storage
4. **Security**: Uploads folder is protected from direct URL access

## Environment Variables

### For Production (Cloudinary)
```bash
# Set environment to production
export FLASK_ENV=production
# or
export ENVIRONMENT=production

# Cloudinary credentials
export CLOUDINARY_CLOUD_NAME=your_cloud_name
export CLOUDINARY_API_KEY=your_api_key
export CLOUDINARY_API_SECRET=your_api_secret
export CLOUDINARY_FOLDER=life-dashboards  # Optional, defaults to 'life-dashboards'
```

### For Development (Local Storage)
```bash
# Set environment to development (default)
export FLASK_ENV=development
# or leave unset

# Local upload folder (optional)
export UPLOAD_FOLDER=/path/to/uploads  # Defaults to ./uploads
```

## How It Works

1. **Development Mode**: Files are stored locally in the `uploads/` folder with user-specific subdirectories
2. **Production Mode**: Files are uploaded to Cloudinary and URLs are stored in the database
3. **File Access**: 
   - Cloud files: Direct redirect to Cloudinary URL
   - Local files: Served through the `/files/view/<id>` route
4. **Security**: Direct access to `/uploads/` folder is blocked and redirects to files list

## File Types Supported

The application supports the following file types:
- Images: png, jpg, jpeg, gif
- Documents: pdf, doc, docx, ppt, pptx
- Text: txt, md

## Usage

1. Upload files through the categories/subpages interface
2. View files in the files list page with "View" and "Download" buttons
3. Files are automatically stored in the appropriate location based on environment
