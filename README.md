# Notion Clone - Flask Web Application

A responsive, feature-rich web application inspired by Notion, built with Flask and modern web technologies. Create, organize, and manage your notes, documents, and projects in a beautiful, intuitive interface.

## ✨ Features

### 🔐 User Authentication
- **Secure Registration & Login**: Session-based authentication with Flask-Login
- **User Management**: Personal workspaces for each user
- **Remember Me**: Optional persistent login sessions

### 🏠 Dashboard & Workspaces
- **Interactive Dashboard**: Overview of all your workspaces and recent activity
- **Category Management**: Create unlimited workspaces (categories) with custom icons and colors
- **Quick Stats**: Visual overview of your content and activity

### 📄 Dynamic Content Management
- **Rich Text Editor**: Powered by Quill.js with full WYSIWYG support
- **Content Blocks**: Modular content system like Notion
- **Nested Pages**: Unlimited subpages within any page
- **Page Templates**: Pre-built templates for common use cases
- **Auto-save**: Automatic content saving every 2 seconds

### 📁 File Management
- **File Uploads**: Support for images, PDFs, documents, and more
- **Drag & Drop**: Intuitive file upload interface
- **Image Preview**: Automatic image preview and display
- **File Organization**: Files automatically organized by user and page

### 🔍 Search & Discovery
- **Global Search**: Search across all pages and content
- **Smart Results**: Search by title, content, and categories
- **Quick Access**: Recent pages and frequently used content

### 🗑️ Trash & Recovery
- **Soft Delete**: Move items to trash instead of permanent deletion
- **Recovery System**: Restore deleted pages and categories
- **Permanent Delete**: Option to permanently remove items

### 🎨 Modern UI/UX
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark Mode**: Toggle between light and dark themes
- **Bootstrap 5**: Modern, accessible design components
- **Smooth Animations**: Elegant transitions and micro-interactions
- **Mobile-First**: Optimized for mobile devices with collapsible sidebar

### 🚀 Technical Features
- **RESTful API**: JSON API for all CRUD operations
- **Real-time Updates**: Live content synchronization
- **Modular Architecture**: Clean separation with Flask Blueprints
- **Database Flexibility**: SQLite for development, easily scalable to PostgreSQL/MySQL
- **CSRF Protection**: Secure forms with CSRF tokens
- **File Security**: Secure file uploads with type validation

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Quill.js, Vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **File Storage**: Local filesystem with organized structure
- **Icons**: Bootstrap Icons
- **Authentication**: Session-based with Flask-Login

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd notion-clone
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export DATABASE_URL="sqlite:///notion_clone.db"
   ```

5. **Initialize the database**
   ```bash
   python app.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## 🗂️ Project Structure

```
notion-clone/
├── app.py                 # Main application file
├── models.py             # Database models
├── forms.py              # WTForms definitions
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── routes/              # Flask blueprints
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── main.py          # Main dashboard routes
│   ├── categories.py    # Category/workspace routes
│   ├── pages.py         # Page management routes
│   └── api.py           # API endpoints
├── templates/           # Jinja2 templates
│   ├── base.html        # Base template
│   ├── auth/            # Authentication templates
│   ├── main/            # Dashboard templates
│   ├── categories/      # Category templates
│   ├── pages/           # Page templates
│   └── errors/          # Error pages
└── static/              # Static assets
    ├── css/
    │   └── style.css    # Custom styles
    ├── js/
    │   └── app.js       # Application JavaScript
    └── uploads/         # User uploaded files
```

## 🎯 Usage Guide

### Getting Started
1. **Register an account** or log in if you already have one
2. **Create your first workspace** by clicking "New Category"
3. **Add pages** to your workspace to start organizing content
4. **Use the rich editor** to create beautiful, formatted content
5. **Upload files** by dragging them into the upload area
6. **Search** your content using the global search bar

### Creating Content
- **Pages**: Create unlimited pages within any workspace
- **Subpages**: Organize content hierarchically with nested pages
- **Rich Text**: Use the toolbar for formatting (headers, lists, quotes, etc.)
- **Files**: Upload and embed images, documents, and other files
- **Templates**: Choose from pre-built templates for common use cases

### Organization
- **Workspaces**: Group related pages into themed workspaces
- **Custom Icons**: Use emojis to personalize your workspaces and pages
- **Color Coding**: Assign colors to workspaces for visual organization
- **Search**: Quickly find any content across all your workspaces

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for security (generate a random string)
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `UPLOAD_FOLDER`: Custom upload directory (optional)

### Production Deployment
For production deployment, consider:
- Using PostgreSQL or MySQL instead of SQLite
- Setting up proper file storage (AWS S3, etc.)
- Configuring reverse proxy (Nginx)
- Using WSGI server (Gunicorn, uWSGI)
- Setting up SSL/HTTPS

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎉 Features Roadmap

- [ ] **Real-time collaboration**: Multiple users editing simultaneously
- [ ] **Database export**: Export content to various formats
- [ ] **API documentation**: Complete REST API documentation
- [ ] **Mobile app**: Native mobile applications
- [ ] **Plugin system**: Extensible plugin architecture
- [ ] **Advanced templates**: More specialized page templates
- [ ] **Team workspaces**: Shared workspaces for collaboration
- [ ] **Version history**: Track and restore previous versions
- [ ] **Calendar integration**: Built-in calendar and scheduling
- [ ] **Task management**: Advanced todo lists and project management

## 🆘 Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page for existing solutions
2. Create a new issue with detailed information
3. Provide steps to reproduce any bugs
4. Include your environment details (OS, Python version, etc.)

---

**Built with ❤️ using Flask and modern web technologies**