import aiohttp

async def fetch_fandom_summary(query):
    # Step 1: Search for the correct sub-wiki
    search_url = "https://community.fandom.com/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, params=params) as response:
            data = await response.json()
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                return None, None

            # Get the title and page ID of the first result
            page_title = search_results[0]["title"]
            
            # Step 2: Find the sub-wiki's domain
            subwiki_url = f"https://{query.replace(' ', '-').lower()}.fandom.com/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "extracts|pageimages",
                "exintro": True,
                "explaintext": True,
                "pithumbsize": 300
            }

            async with session.get(subwiki_url, params=params) as response:
                data = await response.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    summary = page_data.get("extract", "No summary available.")
                    thumbnail = page_data.get("thumbnail", {}).get("source", None)
                    page_url = f"https://{query.replace(' ', '-').lower()}.fandom.com/wiki/{page_title.replace(' ', '_')}"
                    return summary, thumbnail, page_url

    return None, None, None
