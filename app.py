import streamlit as st
import pandas as pd
import requests
import re
import math
import html
from urllib.parse import urlparse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


# Constants
REPO_URL = "https://repo.anaconda.com/pkgs/snowflake/"
CACHE_DURATION = timedelta(hours=1)
ITEMS_PER_PAGE = 15

# CSP Headers - Define allowed sources
CSP_POLICY = {
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self' 'unsafe-inline'",  # Needed for Streamlit
    'img-src': "'self' data:",
    'connect-src': "'self'",
    'font-src': "'self'",
    'frame-ancestors': "'none'",
    'form-action': "'self'"
}

def sanitize_url(url, allowed_domains=None):
    """Sanitize and validate URLs against allowed domains."""
    if not url:
        return ""
    
    if allowed_domains is None:
        allowed_domains = {
            'repo.anaconda.com',
            'github.com',
            'docs.snowflake.com'
        }
    
    try:
        parsed = urlparse(url)
        if parsed.netloc in allowed_domains:
            return url
        return ""
    except:
        return ""

def sanitize_text(text):
    """Sanitize text content to prevent XSS."""
    if not text:
        return ""
    return html.escape(str(text))

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_package_data():
    """Fetch and parse package data from Snowflake's Anaconda channel."""
    try:
        response = requests.get(REPO_URL, timeout=10)
        response.raise_for_status()
        return parse_package_data(response.text)
    except requests.RequestException as e:
        st.error(f"Error fetching package data: {sanitize_text(str(e))}")
        return pd.DataFrame()

def parse_package_data(html_content):
    """Parse the HTML content from Snowflake's Anaconda channel."""
    soup = BeautifulSoup(html_content, 'html.parser')
    packages = []
    
    for row in soup.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if not cols:
            continue
            
        # Get and sanitize documentation and development links
        doc_link = cols[2].find('a') if len(cols) > 2 else None
        dev_link = cols[3].find('a') if len(cols) > 3 else None
        
        package_info = {
            'package_name': sanitize_text(cols[0].text.strip() if cols else ''),
            'version': sanitize_text(cols[1].text.strip() if len(cols) > 1 else ''),
            'documentation': sanitize_url(doc_link['href'] if doc_link else ''),
            'development': sanitize_url(dev_link['href'] if dev_link else ''),
            'license': sanitize_text(cols[4].text.strip() if len(cols) > 4 else ''),
            'summary': sanitize_text(cols[11].text.strip() if len(cols) > 11 else '')
        }
        packages.append(package_info)
    
    return pd.DataFrame(packages)

def filter_packages(df, search_term, license_filter):
    """
    Filter packages based on search criteria with secure text handling
    """
    # Create a copy to avoid modifying original
    filtered_df = df.copy()
    
    # Apply search filter if term exists
    if search_term:
        # Sanitize search term and create case-insensitive pattern
        safe_search_term = re.escape(sanitize_text(search_term))
        pattern = re.compile(safe_search_term, re.IGNORECASE)
        
        # Apply search to both package name and summary
        mask = (
            filtered_df['package_name'].str.contains(pattern, na=False) |
            filtered_df['summary'].str.contains(pattern, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Apply license filter if not "All"
    if license_filter != "All":
        # Sanitize license filter
        safe_license = sanitize_text(license_filter)
        filtered_df = filtered_df[filtered_df['license'] == safe_license]
    
    return filtered_df

def create_package_card(pkg):
    """Create a safe package display card without HTML injection."""
    st.header(f"📦 {pkg['package_name']}")
    
    # Description and basic info
    st.subheader("Description")
    st.info(f"{pkg['summary']}")
    st.markdown(f"**Latest Version**: `{pkg['version']}`")  # Made version display more explicit
    st.markdown(f"**License**: `{pkg['license']}`")
    
    # Installation commands
    st.subheader("Installation Commands")
   
    pip_cmd = f"pip install {pkg['package_name']}"
    conda_cmd = f"conda install -c snowflake {pkg['package_name']}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.code(pip_cmd, language="bash")
        st.caption("For specific version: " + f"pip install {pkg['package_name']}=={pkg['version']}")
        # if st.button(f"Copy pip command ({pkg['package_name']})"):
        #     st.session_state[f"clipboard_{pkg['package_name']}_pip"] = pip_cmd
    
    with col2:
        st.code(conda_cmd, language="bash")
        st.caption("For specific version: " + f"conda install -c snowflake {pkg['package_name']}=={pkg['version']}")
        # if st.button(f"Copy conda command ({pkg['package_name']})"):
        #     st.session_state[f"clipboard_{pkg['package_name']}_conda"] = conda_cmd
    
    # Links
    if pkg['documentation'] or pkg['development']:
        st.subheader("Links")
        if pkg['documentation']:
            st.link_button("📖 Documentation", pkg['documentation'], use_container_width=True)
        if pkg['development']:
            st.link_button("💻 Source Code", pkg['development'], use_container_width=True)

    # Add note about usage
    st.info("""Note: 
            
- conda and pip can be used for local development. 
- !pip can also be used in Notebooks on Container Runtime for ML. 
- For Streamlit in Snowflake (SIS), Snowflake Notebooks on a Warehouse Runtime, and Python Worksheets, use the Packages menu in Snowsight to install a package.""")

def main():
    st.set_page_config(
        page_title="Snowflake Conda Channel Package Explorer",
        page_icon="❄️",
        layout="wide"
    )

    st.title("Snowflake Conda Channel Explorer 🔍❄️")
    with st.expander("💡 About this application"):
        st.write("""
## Overview
Welcome to the Snowflake Conda Channel Explorer! This application helps you easily search through Python packages supported and maintained by Anaconda specifically for Snowflake environments. Search by package name or description to find the tools you need.

## About the Snowflake Conda Channel
The Snowflake Conda channel provides a curated collection of Python packages optimized for Snowflake environments. By using this channel, you agree to Anaconda's Embedded End Customer Terms of Service.

## Package Availability & Usage

### Where You Can Use These Packages
✅ Python Stored Procedures  
✅ Python UDFs (including Vectorized)  
✅ Python UDTFs (including Vectorized)  
✅ Python UDAFs  
✅ Streamlit in Snowflake  
✅ Snowflake Notebooks  

### Important Notes
- **Cost**: No additional charges beyond Snowflake's standard consumption-based pricing
- **SPCS Limitation**: Currently not supported in Snowpark Container Services (SPCS), except for Snowflake Notebooks
  - *Alternative*: For SPCS, install packages from PyPI using pip

## Documentation Links
### Development Guides
- [Python Stored Procedures](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-python)
- [Python UDFs - Introduction](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-introduction)
- [Python UDFs - Vectorized](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-batch)
- [Python UDTFs](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-tabular-functions)
- [Python UDTFs - Vectorized](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-tabular-vectorized)
- [Python UDAFs](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-aggregate-functions)

## Resources
- **Package Directory**: Browse all available packages at [Anaconda Snowflake Channel](https://repo.anaconda.com/pkgs/snowflake)

## Request New Packages
Want a package that's not available? Here's how to request it:

1. Visit the [Snowflake Ideas page](https://community.snowflake.com/s/ideas/)
2. Check the **Packages & Libraries** category for existing requests
3. Either:
   - Vote on existing package requests, or
   - Click **New Idea** to submit a new package request

## To Query Available Packages From within Snowflake
#### Simple
```sql
select * from information_schema.packages;
```
#### Create a view
```sql
-- list of packages and versions
create or replace view anaconda_package_catalog
    comment = 'This custom view references the Information Schema "packages" view and displays a row for each Snowpark package version supported for use in the PACKAGES clause in the CREATE FUNCTION and CREATE PROCEDURE commands. For Python, this view also displays an array of each version of a third-party package that you can install. "package_info" contains a url to learn more about the package'
as
select 
     package_name
    ,language
    ,runtime_version
    ,case 
        when language = 'python'
            then 'https://anaconda.org/anaconda/'||package_name
        when language in ('java','scala')
            then 'https://search.maven.org/artifact/'
                ||split_part(package_name, ':', 1)
                ||'/'
                ||split_part(package_name, ':', 2)
            else null
        end as package_info_url
    ,count(*) as version_count
    ,array_agg(version) as version_list
from snowflake.information_schema.packages 
group by all
order by 2, 3, 1;
```


""")
    
    # Initialize session states
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'last_search' not in st.session_state:
        st.session_state.last_search = None
    if 'last_license' not in st.session_state:
        st.session_state.last_license = None

    # Load data with error handling
    with st.spinner("Loading package data..."):
        df = fetch_package_data()
        
    if df.empty:
        st.error("Unable to load package data. Please try again later.")
        return

    # Sidebar filters
    with st.sidebar:
        st.title("Package Filters")
        
        search_term = st.text_input(
            "Search packages",
            placeholder="Search package name or description...",
            help='Seach package names and package descriptions.',
        )
        
        licenses = ["All"] + sorted(df['license'].unique().tolist())
        license_filter = st.selectbox("License", licenses)
        
        st.divider()
        
        # Statistics
        st.subheader("Statistics")
        st.metric("Total Packages", len(df))
        st.metric("Unique Licenses", len(df['license'].unique()))

        # Helpful links
        st.subheader("Useful Links")
        st.link_button("🐍 Snowpark Developer Guide", "https://docs.snowflake.com/developer-guide/snowpark/python/index", use_container_width=True)
        st.link_button("❄️ About Streamlit in Snowflake", "https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit", use_container_width=True)
        st.link_button("📓 About Snowflake Notebooks", "https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks", use_container_width=True)
        st.link_button("✨ Snowflake ML", "https://docs.snowflake.com/en/developer-guide/snowflake-ml/overview", use_container_width=True)
        st.link_button("🧠 Snowflake Cortex (LLM)", "https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions", use_container_width=True)
    
    # Check if filters have changed
    if (search_term != st.session_state.last_search or 
        license_filter != st.session_state.last_license):
        st.session_state.current_page = 1
        st.session_state.last_search = search_term
        st.session_state.last_license = license_filter

    # Apply filters and display results
    filtered_df = filter_packages(df, search_term, license_filter)

    # Pagination
    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    # Results header
    st.subheader(f"Search Results ({total_items} packages found)")
    
    # Pagination info
    st.text(f"Page {st.session_state.current_page} of {total_pages}")
    st.text(f"Showing items {start_idx + 1}-{min(end_idx, total_items)} of {total_items}")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Previous", type="primary", use_container_width=True, disabled=st.session_state.current_page <= 1):
            st.session_state.current_page = max(1, st.session_state.current_page - 1)
            st.rerun()
    with col2:
        if st.button("Next ⮕", type="primary", use_container_width=True, disabled=st.session_state.current_page >= total_pages):
            st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
            st.rerun()

    # Display packages
    page_df = filtered_df.iloc[start_idx:end_idx]
    for _, pkg in page_df.iterrows():
        with st.expander(f"📦 {sanitize_text(pkg['package_name'])}"):
            create_package_card(pkg)

    # Footer
    st.divider()

    st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()