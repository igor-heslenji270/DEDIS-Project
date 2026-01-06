import streamlit as st
import requests
import pandas as pd
from requests.exceptions import ConnectionError, Timeout

API_URL = "http://127.0.0.1:8000"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None


def check_api_connection():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/docs", timeout=2)
        return True
    except:
        return False

st.set_page_config(page_title="Microbiome Taxonomy Browser", layout="wide")
st.title("Microbiome Taxonomy Browser")

# Check API connection
if not check_api_connection():
    st.error("Cannot connect to FastAPI backend! Make sure it's running on http://127.0.0.1:8000")
    st.info("Run: `uvicorn app.api:app --reload` in your terminal")
    st.stop()

# Sidebar for authentication
with st.sidebar:
    st.header("Authentication")
    
    if not st.session_state.logged_in:
        action = st.radio("Choose action:", ["Login", "Register"])
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if action == "Register":
            if st.button("Register", use_container_width=True):
                if username and password:
                    try:
                        response = requests.post(
                            f"{API_URL}/users/", 
                            json={"username": username, "password": password},
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.success("Registered! Please login.")
                        else:
                            st.error(response.json().get("detail", "Error"))
                    except ConnectionError:
                        st.error("Cannot connect to API. Is FastAPI running?")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please fill in all fields")
        
        else:  # Login
            if st.button("Login", use_container_width=True):
                if username and password:
                    try:
                        response = requests.post(
                            f"{API_URL}/login",
                            json={"username": username, "password": password},
                            timeout=5
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.logged_in = True
                            st.session_state.username = data["username"]
                            st.session_state.user_id = data["user_id"]
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    except ConnectionError:
                        st.error("Cannot connect to API. Is FastAPI running?")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please fill in all fields")
    
    else:
        st.success(f" **{st.session_state.username}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()

# Main content
if not st.session_state.logged_in:
    st.info("Please log in to access the browser.")
else:
    tab1, tab2, tab3 = st.tabs(["My Samples", "Add Sample", "Search"])
    
    # TAB 1: My Samples
    with tab1:
        st.header("My Microbiome Samples")
        
        try:
            response = requests.get(f"{API_URL}/samples/user/{st.session_state.user_id}")
            if response.status_code == 200:
                samples = response.json()
                
                if samples:
                    for sample in samples:
                        with st.expander(f" {sample['name']}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**Taxonomy:** {sample['taxonomy']}")
                                st.write(f"**Abundance:** {sample['abundance']:.2f}%")
                                st.write(f"**Location:** {sample['location']}")
                            
                            with col2:
                                if st.button(" Delete", key=f"del_{sample['id']}"):
                                    del_response = requests.delete(
                                        f"{API_URL}/samples/{sample['id']}",
                                        params={"user_id": st.session_state.user_id}
                                    )
                                    if del_response.status_code == 200:
                                        st.success("Deleted!")
                                        st.rerun()
                    
                    # Table view
                    st.subheader("Sample Table")
                    df = pd.DataFrame(samples)
                    st.dataframe(df[['name', 'taxonomy', 'abundance', 'location']], use_container_width=True)
                else:
                    st.info("No samples yet. Add your first sample!")
        except Exception as e:
            st.error(f"Error loading samples: {e}")
    
    # TAB 2: Add Sample
    with tab2:
        st.header("Add New Sample")
        
        with st.form("add_sample_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sample_name = st.text_input("Sample Name*", placeholder="Sample_001")
                taxonomy = st.text_input("Taxonomy*", placeholder="Bacteria;Proteobacteria")
            
            with col2:
                abundance = st.number_input("Abundance (%)*", 0.0, 100.0, 0.0, 0.1)
                location = st.text_input("Location*", placeholder="Gut, Soil, Ocean")
            
            submitted = st.form_submit_button("Add Sample", use_container_width=True)
            
            if submitted:
                if sample_name and taxonomy and location:
                    try:
                        response = requests.post(
                            f"{API_URL}/samples/",
                            params={"user_id": st.session_state.user_id},
                            json={
                                "name": sample_name,
                                "taxonomy": taxonomy,
                                "abundance": abundance,
                                "location": location
                            },
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.success("Sample added!")
                        else:
                            error_detail = response.json().get("detail", "Unknown error")
                            st.error(f"Failed to add sample: {error_detail}")
                            st.error(f"Status code: {response.status_code}")
                    except ConnectionError:
                        st.error("Cannot connect to API")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please fill all fields")
    
    # TAB 3: Search with Strategy Pattern
    with tab3:
        st.header("Advanced Search")
        
        st.info("**Strategy Pattern Demo**: Choose different search algorithms at runtime!")
        
        # Strategy selector
        strategy = st.selectbox(
            "Select Search Strategy:",
            ["exact", "approximate", "hierarchical", "abundance"],
            format_func=lambda x: {
                "exact": "Exact Match",
                "approximate": "Approximate Match", 
                "hierarchical": "Hierarchical Match",
                "abundance": "Abundance Filter"
            }[x],
            help="Each strategy uses a different algorithm to find samples"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("Search Term", placeholder="e.g., Bacteria or Proteobacteria")
        
        # Additional parameters for abundance filter
        min_abundance = 0.0
        max_abundance = 100.0
        if strategy == "abundance":
            with col2:
                min_abundance = st.number_input("Min Abundance (%)", 0.0, 100.0, 0.0)
                max_abundance = st.number_input("Max Abundance (%)", 0.0, 100.0, 100.0)
        
        if st.button("Search", use_container_width=True):
            if search_query or strategy == "abundance":
                try:
                    # Single API endpoint with strategy parameter
                    response = requests.get(
                        f"{API_URL}/search",
                        params={
                            "query": search_query,
                            "strategy": strategy,
                            "min_abundance": min_abundance,
                            "max_abundance": max_abundance
                        }
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        if results:
                            strategy_name = {
                                "exact": "Exact Match",
                                "approximate": "Approximate Match",
                                "hierarchical": "Hierarchical Match",
                                "abundance": "Abundance Filter"
                            }[strategy]
                            
                            st.success(f"Found {len(results)} samples using **{strategy_name}**")
                            
                            for sample in results:
                                with st.container():
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.markdown(f"**{sample['name']}**")
                                    with col2:
                                        st.write(f"Taxonomy: {sample['taxonomy']}")
                                    with col3:
                                        st.write(f"Abundance: {sample['abundance']:.2f}%")
                                    st.divider()
                        else:
                            st.info("No samples found")
                    else:
                        st.error(f"Search failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Search error: {e}")
            else:
                st.warning("Please enter a search term")
        
        # Explanation of strategies
        with st.expander("About Search Strategies"):
            st.markdown("""
            **Strategy Pattern** allows you to define different algorithms and switch between them at runtime.
            
            **Available Strategies:**
            - **Exact Match**: Finds samples where the taxonomy contains the exact search term
            - **Approximate Match**: Uses similarity scoring to find approximate matches (60% threshold)
            - **Hierarchical Match**: Searches by taxonomy hierarchy (e.g., "Bacteria;Proteobacteria")
            - **Abundance Filter**: Filters samples by abundance range and optional taxonomy
            
            All strategies are accessed through a **single API endpoint** (`/search`) with the strategy 
            selected at runtime via the `strategy` parameter. This demonstrates the true Strategy pattern 
            where different algorithms are hidden behind a unified interface.
            """)