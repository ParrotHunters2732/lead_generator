# YellowPages Business Intelligence Scraper

A production-grade business data extraction and management system built with Python, Streamlit, and Supabase. Scrapes, validates, stores, and queries business data from YellowPages at scale.

---

## Results

- 3,000 businesses extracted per run
- 97% website extraction rate
- 100% category hit rate
- 550+ emails extracted via Cloudflare bypass
- 0 failed extractions across full 6-hour deep-scan runs
- Full audit trail via structured logging

---

## Features

- **Business List Extraction** — scrapes name, rating, review count, address, phone, hours, URL
- **Business Insight Extraction** — deep-dives into individual pages for emails, descriptions, payment methods, extra phones, social links
- **Cloudflare Email Decode** — XOR decodes obfuscated email addresses automatically
- **Pydantic Validation** — every AI/scraper output is validated before database injection, no corrupt data
- **SQL Guardrails** — custom query tab blocks all destructive commands (DROP, DELETE, TRUNCATE, UPDATE, INSERT, ALTER)
- **Retry Logic** — automatically retries failed pages, compiles error lists, re-runs after session ends
- **Rate Limiting** — randomized delays between requests to mimic human browsing behavior
- **Connection Pooling** — ThreadedConnectionPool with proper acquire/release lifecycle, no connection leaks
- **Config Management** — all settings editable via UI, validated on save, no manual file editing required
- **Data Filtering** — select specific columns, set row limits, export to CSV
- **Custom SQL Queries** — run your own SELECT/WITH queries with safety constraints
- **Real-time Logs** — view last 100/300/500/1000 log lines directly in the app
- **Database Stats Dashboard** — total rows, missing data %, perfect leads count, legit insight count

---


## Project Structure

```
├── main.py                  # Streamlit app — all pages and navigation
├── utils.py                 # GetAndStoreData — orchestrates scrape + write lifecycle
├── helpers.py               # Config read/write, .env management, Streamlit dialogs
├── decorators.py            # Exception handling + database context manager decorators
├── models.py                # Pydantic models — BusinessListData, BusinessInsightData, ConfigJson
├── retry.py                 # Retry logic for failed pages — strategy pattern
├── config.json              # Scraper configuration (auto-managed via UI)
├── .env                     # Supabase credentials (auto-managed via UI)
├── app.log                  # Runtime logs
├── database/
│   └── supabase.py          # Reader + Writer classes, SQL guardrails
├── scraper/
│   └── yellowpages.py       # YellowPagesScraper — list + insight extraction, Cloudflare decode
└── logs/
    └── log.py               # CustomLogger singleton
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your Supabase project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your **Project ID** and **Database Password**
3. Open the **SQL Editor** in your Supabase dashboard and run the following in order:

```sql
create table public.business_list (
    name text null,
    url text null,
    postal_code text null,
    country text null,
    street text null,
    location_name text null,
    state_code text null,
    rating numeric(2, 1) null,
    review_count integer null,
    telephone text null,
    opening_hours text null,
    unique_key uuid not null default gen_random_uuid (),
    timestamp timestamp with time zone null default (now() AT TIME ZONE 'utc'::text),
    constraint business_list_pkey primary key (unique_key)
) TABLESPACE pg_default;
```

```sql
create table public.business_insight_data (
    name text null,
    category text null,
    description text null,
    address text null,
    website text null,
    phone character varying(30) null,
    email text null,
    payment text null,
    language text null,
    extra_links text null,
    extra_phone text null,
    unique_key uuid not null,
    timestamp timestamp with time zone null default (now() AT TIME ZONE 'utc'::text),
    constraint business_insight_data_pkey primary key (unique_key),
    constraint business_insight_data_unique_key_fkey foreign key (unique_key)
        references business_list (unique_key) on delete cascade
) TABLESPACE pg_default;
```

### 4. Run the app

```bash
streamlit run main.py
```

### 5. Enter your Supabase credentials

Navigate to the **Configuration** page → scroll to **Database Configuration** → click **Enter info** → paste your Project ID and Database Password.

---

## Configuration Guide

All settings are managed via the **Configuration** page in the UI. No manual file editing required.

| Setting | Description | Recommended |
|---|---|---|
| Page per Request | Total pages to scrape per session (~30 businesses/page) | 100 |
| Rate Min | Minimum delay between requests (seconds) | 3.0 |
| Rate Max | Maximum delay between requests (seconds) | 6.25 |
| Max Attempt | Retry limit per failed page | 3 |
| Attempt Duration | Wait time between retries (seconds) | 45.0 |
| Redo on Fail Page | Retry all failed pages after session ends | true |
| Redo Attempt | How many times to retry the failed page list | 2 |
| Category | Business type to search (e.g. accounting, dentist) | — |
| Location | Geographic target (e.g. NYC NY, Los Angeles CA) | — |
| Cookies | YellowPages session cookies for stable requests | recommended |
| Amount for Insight | How many businesses to deep-scan | 100–3000 |

---

## Getting Your Cookies (Recommended)

Cookies significantly improve scrape stability and reduce 403 errors.

1. Open [yellowpages.com](https://www.yellowpages.com) in your browser
2. Install the **Cookie Editor** browser extension
3. Click the extension → select **Export as Header String**
4. Paste the result into the **Cookies** field in Configuration
5. Click **Save**

Refresh your cookies if failure rates spike.

---

## Usage

### Extract Business List

1. Set your **Category** and **Location** in Configuration
2. Go to **Scrape** → **Business List** tab
3. Click **Start Scraping**
4. Progress bar updates per page — ~30 businesses per page, ~100 pages = ~3,000 businesses

### Extract Business Insights

Runs a deep-scan on businesses already in your database that have no insight data yet.

1. Set **Amount for Insight** in Configuration (how many to deep-scan)
2. Go to **Scrape** → **Business Insight** tab
3. Click **Start Scraping**
4. Each business is individually visited — expect ~6–8 hours for 3,000

### View and Filter Data

1. Go to **Data** → **Overall** tab for database stats
2. Go to **Data Selector** tab — choose Business List or Business Insight
3. Click **Filter** → check the columns you want
4. Set a row limit and click **Pull Data**

### Run Custom Queries

1. Go to **Data** → **Custom Query** tab
2. Paste your SQL — only SELECT and WITH statements are allowed
3. Click **Execute**

Example queries:

```sql
-- Get all businesses with emails in New York
SELECT name, telephone, email, website
FROM business_insight_data
WHERE email IS NOT NULL
LIMIT 500;
```

```sql
-- Get high-rated businesses with phone numbers
SELECT name, rating, telephone, url
FROM business_list
WHERE rating >= 4.0
AND telephone IS NOT NULL
ORDER BY rating DESC
LIMIT 100;
```

```sql
-- Find businesses with both email and website
SELECT bl.name, bl.rating, bid.email, bid.website
FROM business_list bl
JOIN business_insight_data bid ON bl.unique_key = bid.unique_key
WHERE bid.email IS NOT NULL
AND bid.website IS NOT NULL
ORDER BY bl.rating DESC;
```

---

## Rules of Operation

- **One session at a time** — do not run two scrapes simultaneously, it causes data conflicts
- **Scrape once per category/location** — rerunning the same target causes high duplicate rates
- **Do not interrupt mid-scrape** — quitting during scraping can result in partial/duplicate data
- **Custom Query tab is read-only** — use it for SELECT only, structural changes go through Supabase dashboard directly
- **Refresh cookies if failures spike** — a stale session cookie is the most common cause of 403 errors

---

## Data Fields Reference

### Business List

| Field | Description |
|---|---|
| name | Business name |
| url | YellowPages listing URL |
| postal_code | ZIP/postal code |
| country | Country code |
| street | Street address |
| location_name | City |
| state_code | State abbreviation |
| rating | Aggregate rating (0.0–5.0) |
| review_count | Total number of reviews |
| telephone | Primary phone number |
| opening_hours | Business hours |
| unique_key | UUID primary key |
| timestamp | UTC timestamp of extraction |

### Business Insight

| Field | Description |
|---|---|
| name | Business name |
| category | Business category/categories |
| description | Business description |
| address | Full street address |
| website | Official website URL |
| phone | Primary phone |
| email | Contact email (Cloudflare-decoded) |
| payment | Accepted payment methods |
| language | Languages spoken |
| extra_links | Social media / secondary links |
| extra_phone | Additional phone numbers |
| unique_key | Foreign key → business_list |
| timestamp | UTC timestamp of extraction |

---

## Legal & Disclaimer

This software is provided "as is" without warranty of any kind. The developer is not responsible for any IP bans, legal disputes, or data loss incurred through use of this tool.

Users are solely responsible for ensuring scraping activities comply with the target website's Terms of Service and applicable local privacy laws (GDPR, CCPA, etc.).

This tool is designed for internal lead generation purposes. Unauthorized redistribution of this software or commercial resale of scraped data without proper authorization is prohibited.

Use at your own risk.

---

## License

MIT License — see LICENSE file for details.
