# Snowflake Conda Channel Package Explorer 🔍❄️

A Streamlit application that provides an easy-to-use interface for exploring Python packages available in Snowflake's Anaconda channel. This tool helps developers quickly find, understand, and use packages supported in Snowflake's Python environments.

## 🌟 Features

- **Interactive Package Search**: Search through packages by name and description
- **License Filtering**: Filter packages based on their license type
- **Detailed Package Information**: 
  - Package descriptions and versions
  - Installation commands for both pip and conda
  - Direct links to documentation and source code
  - License information
- **Pagination**: Easy navigation through large sets of packages
- **Security Features**: 
  - URL sanitization
  - Content sanitization
  - CSP headers implementation
- **Responsive Design**: Works well on both desktop and mobile devices

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

## 🚀 Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/snowflake-package-explorer.git
   cd snowflake-package-explorer
   ```

2. **Create and Activate Virtual Environment (Optional but Recommended)**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access the Application**
   - Open your web browser and navigate to `http://localhost:8501`

## 🛠️ Usage

1. **Search Packages**
   - Use the search box in the sidebar to find packages by name or description
   - Results update automatically as you type

2. **Filter by License**
   - Select a license type from the dropdown menu in the sidebar
   - Choose "All" to view packages with any license

3. **View Package Details**
   - Click on a package card to expand and view detailed information
   - Copy installation commands directly from the interface
   - Access documentation and source code through provided links

## 📦 Package Information

The application displays the following information for each package:
- Package name and version
- Description/summary
- License
- Installation commands (pip and conda)
- Documentation links
- Source code repository links
- Usage notes specific to Snowflake environments

## 🔐 Security Features

The application implements several security measures:
- URL sanitization for external links
- Content sanitization to prevent XSS attacks
- Restricted domain allowlist
- Content Security Policy (CSP) headers
- Cache control for API requests

## 🔧 Configuration

Key configurations can be modified in the constants section at the top of `app.py`:
- `REPO_URL`: The base URL for the Snowflake Anaconda repository
- `CACHE_DURATION`: How long to cache package data
- `ITEMS_PER_PAGE`: Number of packages to display per page

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Snowflake for providing the Anaconda channel
- Streamlit for the amazing web app framework
- The Python community for the various packages used in this project

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/snowflake-package-explorer/issues) page
2. Create a new issue with a detailed description of your problem
3. For Snowflake-specific questions, refer to the [Snowflake Documentation](https://docs.snowflake.com/)

---
Made with ❄️ for the Snowflake community
