import requests
from neo4j import GraphDatabase

# The exact URL you verified in your browser
VERIFIED_URL = "https://data.kingcounty.gov/api/v3/views/sep3-3pj3/query.json?pageNumber=1&pageSize=200&app_token=rQbRdnzj0KI8a61Zqq07LBPoY"


def final_mission_ingest():
    print(f"Executing Master Pull from: {VERIFIED_URL}")

    # Simple GET request since the URL already contains all your parameters
    response = requests.get(VERIFIED_URL)
    response.raise_for_status()
    providers = response.json()

    print(f"Successfully retrieved {len(providers)} BH Provider records.")

    # --- NEO4J SYNC ---
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password123"))

    # Mapping exactly to the King County BH Provider schema
    query = """
    UNWIND $batch AS item
    // Use COALESCE to provide a fallback if site_name or agency_name is null
    MERGE (p:Provider {
        agency: COALESCE(item.agency_name, "Unknown Agency"),
        site: COALESCE(item.site_name, "Unknown Site")
    })
    SET p.phone = item.phone_number,
        p.address = item.full_address,
        p.zip = item.zip_code,
        p.mental_health = item.mental_health,
        p.substance_use = item.substance_use_disorder,
        p.is_public = true,
        p.user_id = 'PUBLIC',
        p.last_updated = datetime(),
        p.batch_id = "Initial_KC_Ingest"
    """

    with driver.session() as session:
        session.run(query, batch=providers)

    driver.close()
    print("Mission Success: The Vault is now populated with live King County data.")


# Run the final ingest
final_mission_ingest()
