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
                job_listings = soup.find_all('div', class_='career-opening')
                
                for job in job_listings:
                    title_elem = job.find('h3')
                    link_elem = job.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem.get('href')
                        jobs.append({
                            'title': title,
                            'company': 'Cylinder Health',
                            'location': 'Remote',
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
                content = response.text
                
                # Extract job listings using regex pattern matching
                # Looking for patterns like "425 - Software Development" and subsequent job titles
                departments = re.finditer(r'(\d+)\s*-\s*([^\n]+)', content)
                
                current_dept = None
                for dept in departments:
                    dept_id = dept.group(1)
                    dept_name = dept.group(2).strip()
                    
                    # Find jobs under this department
                    # Looking for job titles in bold (**) followed by location
                    job_pattern = r'\*\*([^*]+)\*\*\s*([^*\n]+)?'
                    job_matches = re.finditer(job_pattern, content[dept.end():])
                    
                    for job in job_matches:
                        title = job.group(1).strip()
                        location = job.group(2).strip() if job.group(2) else "Remote, USA"
                        
                        # Skip if this looks like a header
                        if title.lower() in ['search', 'department', 'office']:
                            continue
                            
                        jobs.append({
                            'title': title,
                            'company': 'MedAnalytics',
                            'location': location,
                            'link': url,
                            'department': dept_name,
                            'source': 'MedAnalytics'
                        })
                        
                st.write(f"Found {len(jobs)} jobs at MedAnalytics")  # Debug output
                
        except Exception as e:
            st.error(f"Error scraping MedAnalytics: {str(e)}")
            st.error(f"Response status: {response.status_code if 'response' in locals() else 'No response'}")
        
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
    show_all_departments = st.checkbox("Show all departments (not just AI/Data Science)", value=True)
    
    if st.button("Scan for Jobs"):
        with st.spinner("Scanning company career pages..."):
            all_jobs = []
            
            if "Cylinder Health" in companies:
                cylinder_jobs = scraper.scrape_cylinder_health()
                st.write(f"Found {len(cylinder_jobs)} jobs at Cylinder Health")  # Debug output
                all_jobs.extend(cylinder_jobs)
            
            if "MedAnalytics" in companies:
                medanalytics_jobs = scraper.scrape_medanalytics()
                all_jobs.extend(medanalytics_jobs)
            
            if all_jobs:
                # Convert to DataFrame
                df = pd.DataFrame(all_jobs)
                
                # Filter for AI/Data Science positions if checkbox is not checked
                if not show_all_departments:
                    ai_keywords = ['data', 'ai', 'machine learning', 'analyst', 'scientist', 'analytics', 
                                 'artificial intelligence', 'nlp', 'neural', 'devops', 'engineer']
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
                
                # Show raw job data for debugging
                if st.checkbox("Show raw job data"):
                    st.json(all_jobs)
                
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
