KING COUNTY DATA SETS

https://data.kingcounty.gov/api/v3/views/<dataset_id>/query.json?pageNumber=1&pageSize=200&app_token=<token_placeholder>

KING_COUNTY_211_APP_TOKEN=<token_placeholder>


1. General Human Services Providers & Basic Needs
This is the primary dataset containing programs for food assistance, cash support, clothing, hygiene facilities, and basic survival items. 
Dataset ID: x6fc-6pka

2. Affordable Housing & Emergency Overnight Shelters
Contains active regional shelter inventories, temporary housing assistance options, and emergency placement capacities. 
Dataset ID: g673-8gsh

3. Public Health Centers, Clinics & Mobile Dental Services
Maps community dental vans, free medical clinics, and public medical providers offering sliding-scale fees. 
Dataset ID: vgh2-9egh

4. Eviction Prevention & Emergency Rent Assistance Performance
Tracks rental grants, emergency cash intervention points, and legal aid programs preventing physical displacement. 
Dataset ID: 6473-b8y5

1. Approximate Size BreakdownBecause the records are structured text objects, the download footprint is minimal:Dataset / IDTotal Rows (Est.)Raw JSON File SizeDownload RiskHuman Services (x6fc-6pka)~1,000 to 2,500 rows2 MB to 5 MBLow (Max row restriction)Shelter Inventory (g673-8gsh)~500 to 1,200 rows1 MB to 3 MBVery LowHealth Clinics (vgh2-9egh)~100 to 300 rows< 1 MBVery Low2. The Problems You Will Run Into (and how to fix them)Problem A: The 1,000-Row Default GateIf you pull the main human services dataset using a standard GET request without specific query parameters, the server will stop sending records precisely at 1,000 rows. This is a safety cap hardcoded into the Socrata platform architecture.The Fix: You must pass the system pagination parameters explicitly. Since your model uses pageSize=200, your app will need a simple loop that increments pageNumber=1, pageNumber=2, and so forth, until the response payload returns empty.Problem B: Rate Throttling Without a TokenIf you loop through pages rapidly using a server-side script, the King County firewalls will assume your app is a malicious scraping bot. They will issue a 429 Too Many Requests or 403 Forbidden error to block your server IP address.The Fix: Ensure your custom script injects a small delay (e.g., 200 to 500 milliseconds) between iterative page requests, and make sure your app_token placeholder contains a verified token generated via the King County Open Data Portal.Problem C: Fluctuating Active Service IDsThese data catalogs are dynamic. Nonprofits shift their operation hours, rename programs, or go out of business entirely. If your application maps local data entries using static array indexes or fixed table IDs, your internal links will break during database updates.The Fix: Always map data associations using the primary tracking keys provided in the payload (such as location_id or program_id), rather than relying on structural row positions.

Other Dataset IDs:

sep3-3pj3: King County Mental Health and Substance Use Disorder Providers Directory.
nqri-czhj: High-priority health interventions and specialized vulnerable population care sites.
mnxa-8m4g: Community and Human Services Calendar (tracks localized outreach events and mobile distribution pop-ups).
2be9-wu5b: Best Starts for Kids Award Database (tracks funded youth family resource points and early intervention sites).64yn-5kas: King County Metro - Solid Ground Circulator (tracks targeted public transit routes shuttling individuals directly to local social service agencies).

The Global Catalog Endpoint
Instead of guessing individual 4x4 IDs, your application can ping Socrata's discovery engine to fetch a complete JSON array of every dataset, view, and API endpoint hosted by King County.You can load this URL directly in your browser or code environment (no token placeholder required): https://kingcounty.gov(the rest of the URL is trucated by Gemini)

Use code with caution.What this returns: A massive root-level JSON list. Each object in the array represents a unique dataset containing its active id, structural name, description, data tags, and exact creation timestamps.

https://dev.socrata.com/docs/endpoints

https://cos-data.seattle.gov/api/v3/views/kkzf-ntnu/query.json?accessType=DOWNLOAD

https://cos-data.seattle.gov/resource/uxxb-mmuq.json
uxxb-mmuq

https://data.kingcounty.gov/
https://openreferral.org/
https://www.dshs.wa.gov/

https://api.211.org/v1/openreferral/
