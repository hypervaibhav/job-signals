import requests
from bs4 import BeautifulSoup
from collections import Counter
from database import init_db, save_jobs


def scrape_indeed(query="customer support", location="Toronto"):
    print("Trying Indeed...")

    url = f"https://ca.indeed.com/jobs?q={query}&l={location}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)

        print("Indeed status:", res.status_code)

        if res.status_code != 200:
            print("Indeed blocked or failed. Falling back...")
            return []

        soup = BeautifulSoup(res.text, "html.parser")

        jobs = []

        cards = soup.find_all("div", class_="job_seen_beacon")

        for card in cards:
            title_tag = card.find("h2")
            company_tag = card.find("span", class_="companyName")

            title = title_tag.text.strip() if title_tag else "N/A"
            company = company_tag.text.strip() if company_tag else "N/A"

            jobs.append({
                "title": title,
                "company": company,
                "source": "indeed",
                "description": "",
            })

        return jobs

    except Exception as e:
        print("Indeed error:", e)
        return []


def scrape_remotive():
    print("Using Remotive API...")

    url = "https://remotive.com/api/remote-jobs"
    res = requests.get(url, timeout=10)

    data = res.json()

    jobs = []

    for job in data["jobs"][:20]:
        description_html = job.get("description", "")
        description = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)

        jobs.append({
            "title": job["title"],
            "company": job["company_name"],
            "source": "remotive",
            "description": description,
        })

    return jobs


def scrape_remoteok():
    print("Using RemoteOK API...")

    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JobSignalsBot/1.0)"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        print("RemoteOK status:", res.status_code)

        if res.status_code != 200:
            print("RemoteOK failed. Skipping...")
            return []

        data = res.json()
        jobs = []

        for job in data[1:21]:
            title = job.get("position") or job.get("title") or "N/A"
            company = job.get("company") or "N/A"
            description_html = job.get("description", "")
            description = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)

            jobs.append({
                "title": title,
                "company": company,
                "source": "remoteok",
                "description": description,
            })

        return jobs

    except Exception as e:
        print("RemoteOK error:", e)
        return []


def scrape_greenhouse():
    print("Using Greenhouse API...")

    boards = [
        "stripe",
        "reddit",
        "canva",
        "datadog",
        "discord",
    ]

    jobs = []

    for board in boards:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"

        try:
            res = requests.get(url, timeout=10)

            if res.status_code != 200:
                continue

            data = res.json()

            for job in data.get("jobs", [])[:10]:
                jobs.append(
                    {
                        "title": job.get("title", "N/A"),
                        "company": board.title(),
                        "source": "greenhouse",
                        "external_id": str(job.get("id", "")),
                        "description": "",
                    }
                )

        except Exception as e:
            print(f"Greenhouse error ({board}):", e)

    return jobs


def generate_signals(jobs):
    print("\n--- SIGNALS ---\n")

    companies = Counter([job["company"] for job in jobs])
    titles = Counter([job["title"] for job in jobs])

    print("Top Hiring Companies:")

    for company, count in companies.most_common(5):
        print(f"- {company}: {count} postings")

    print("\nMost Common Roles:")

    for title, count in titles.most_common(5):
        print(f"- {title}: {count} postings")


if __name__ == "__main__":
    init_db()

    jobs = []
    jobs.extend(scrape_remotive())
    jobs.extend(scrape_remoteok())
    jobs.extend(scrape_greenhouse())

    print("\n--- JOBS FOUND ---\n")

    for job in jobs:
        print(f"{job['title']} — {job['company']} [{job['source']}]")

    save_jobs(jobs)

    generate_signals(jobs)
