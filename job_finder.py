# utils/job_finder.py

import requests



def fetch_jobs(skills, location):
    try:
        if not skills or not location:
            return [{"error": "Missing skills or location for job search."}]
        
        query = "+".join(skills[:3])  # use top 3 skills to build the query
        location = location.replace(" ", "+")
        url = f"https://remotive.io/api/remote-jobs?search={query}&location={location}"

        response = requests.get(url, timeout=10)

        # Empty or invalid response
        if not response.content:
            return [{"error": "No content returned from job API."}]
        
        data = response.json()

        if "jobs" not in data:
            return [{"error": "Unexpected response format from job API."}]
        
        jobs = data["jobs"][:5]  # return top 5 jobs
        result = []
        for job in jobs:
            result.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location"),
                "url": job.get("url")
            })
        return result

    except requests.exceptions.RequestException as e:
        return [{"error": f"Request failed: {str(e)}"}]
    except ValueError as ve:
        return [{"error": f"Failed to decode JSON: {str(ve)}"}]

