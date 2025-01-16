import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

class CompanyJobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def scrape_cylinder_health(self):
        jobs = []
        url = "https://cylinderhealth.com/about-us/careers/#open-positions"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find the jobs section
                job_listings = soup.find_all('div', class_='career-opening')
                
                for job in job_listings:
                    title_elem = job.find('h3')
                    link_elem = job.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get('href')
                        
                        # Only include AI/Data Science related positions
                        if any(keyword in title.lower() for keyword in ['data', 'ai', 'machine learning', 'analyst', 'scientist', 'analytics']):
                            jobs.append({
                                'title': title,
                                'company': 'Cylinder Health',
                                'location': 'Remote',  # Modify if location info becomes available
                                'link': link,
                                'department': 'N/A',
                                'source': 'Cylinder Health'
                            })
        except Exception as e:
            st.error(f"Error scraping Cylinder Health: {str(e)}")
        
        return jobs

    def scrape_medanalytics(self):
        jobs = []
        url = "https://job-boards.greenhouse.io/medeanalytics"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all job sections - they appear to be grouped by department
                departments = soup.find_all(['h3', 'strong'])  # Department headers
                
                current_department = "General"
                for element in soup.find_all(['strong', 'h3', 'p']):
                    text = element.text.strip()
                    
                    # Check if this is a department header
                    if element.name in ['h3', 'strong'] and ' - ' in text:
                        current_department = text.split(' - ')[1].strip()
                        continue
                    
                    # Check if this is a job listing
                    if '**' in text:  # Job titles are marked with **
                        # Extract title and location
                        parts = text.split('**')
                        for part in parts:
                            if part.strip() and not part.startswith(('Department', 'Office', 'Search')):
                                title = part.strip()
                                location = "Remote, USA"  # Default location
                                
                                # Try to extract location if it's in the text
                                location_match = re.search(r'(Remote|Richardson, TX|Nashville, TN|Remote, USA)', text)
                                if location_match:
                                    location = location_match.group(1)
                                
                                jobs.append({
                                    'title': title,
                                    'company': 'MedAnalytics',
                                    'location': location,
                                    'link': url,  # Since individual job links aren't available
                                    'department': current_department,
                                    'source': 'MedAnalytics'
                                })
                
        except Exception as e:
            st.error(f"Error scraping MedAnalytics: {str(e)}")
        
        return jobs

def main():
    st.title("AI & Data Science Job Scraper")
    st.write("Scanning Cylinder Health and MedAnalytics for AI & Data Science positions")
    
    # Initialize scraper
    scraper = CompanyJobScraper()
    
    # Add company selection
    companies = st.multiselect(
        "Select companies to scan",
        ["Cylinder Health", "MedAnalytics"],
        default=["Cylinder Health", "MedAnalytics"]
    )
    
    # Add department filter
    show_all_departments = st.checkbox("Show all departments (not just AI/Data Science)", value=False)
    
    if st.button("Scan for Jobs"):
        with st.spinner("Scanning company career pages..."):
            all_jobs = []
            
            # Create progress bar
            progress_bar = st.progress(0)
            progress_step = 1 / len(companies)
            current_progress = 0
            
            if "Cylinder Health" in companies:
                cylinder_jobs = scraper.scrape_cylinder_health()
                all_jobs.extend(cylinder_jobs)
                current_progress += progress_step
                progress_bar.progress(current_progress)
            
            if "MedAnalytics" in companies:
                medanalytics_jobs = scraper.scrape_medanalytics()
                all_jobs.extend(medanalytics_jobs)
                current_progress += progress_step
                progress_bar.progress(1.0)
            
            if all_jobs:
                # Convert to DataFrame
                df = pd.DataFrame(all_jobs)
                
                # Filter for AI/Data Science positions if checkbox is not checked
                if not show_all_departments:
                    ai_keywords = ['data', 'ai', 'machine learning', 'analyst', 'scientist', 'analytics', 
                                 'artificial intelligence', 'nlp', 'neural']
                    df = df[df['title'].str.lower().str.contains('|'.join(ai_keywords), na=False)]
                
                # Display results
                st.subheader(f"Found {len(df)} Positions")
                
                # Add department filter
                if len(df) > 0:
                    departments = sorted(df['department'].unique())
                    selected_departments = st.multiselect(
                        "Filter by department",
                        departments,
                        default=departments
                    )
                    df = df[df['department'].isin(selected_departments)]
                
                # Display as interactive table
                st.dataframe(df)
                
                # Export option
                if st.download_button(
                    label="Download Results as CSV",
                    data=df.to_csv(index=False),
                    file_name=f"company_job_search_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                ):
                    st.success("Data downloaded successfully!")
            else:
                st.warning("No positions found at selected companies.")

if __name__ == "__main__":
    main()

# Requirements (save as requirements.txt):
"""
streamlit
beautifulsoup4
requests
pandas
"""

# To run the app:
# 1. Save this code as app.py
# 2. Install requirements: pip install -r requirements.txt
# 3. Run: streamlit run app.py
