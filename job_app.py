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
                # Find all job listings
                job_listings = soup.find_all('div', class_='opening')
                
                for job in job_listings:
                    title_elem = job.find('a')
                    location_elem = job.find('span', class_='location')
                    
                    if title_elem:
                        title = title_elem.text.strip()
                        link = f"https://job-boards.greenhouse.io{title_elem.get('href')}"
                        location = location_elem.text.strip() if location_elem else 'Not specified'
                        
                        # Only include AI/Data Science related positions
                        if any(keyword in title.lower() for keyword in ['data', 'ai', 'machine learning', 'analyst', 'scientist', 'analytics']):
                            jobs.append({
                                'title': title,
                                'company': 'MedAnalytics',
                                'location': location,
                                'link': link,
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
                
                # Display results
                st.subheader(f"Found {len(all_jobs)} AI & Data Science Positions")
                
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
                st.warning("No AI or Data Science positions found at selected companies.")

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
