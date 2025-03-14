import wikipedia
import discord

async def fetch_wiki_summary(topic):
    try:
        # Search for pages related to the topic
        search_results = wikipedia.search(topic)
        if not search_results:
            return None  # No results found
        
        # Get the top result and fetch its content
        page = wikipedia.page(search_results[0])

        # Check if topic is mentioned directly in the page title
        summary = page.summary if topic.lower() in page.title.lower() else f"Couldn't find a direct page for '{topic}', but here's info about {page.title}:\n\n{page.summary}"

        # Create a Discord embed
        embed = discord.Embed(title=page.title, description=summary[:2000], color=discord.Color.blue())
        embed.set_footer(text="Read more")
        embed.url = page.url

        return embed

    except wikipedia.exceptions.DisambiguationError as e:
        # Handle ambiguous topics (multiple possible pages)
        options = "\n".join(e.options[:5])  # Show the top 5 options
        embed = discord.Embed(
            title="Disambiguation Error",
            description=f"'{topic}' may refer to multiple pages:\n\n{options}",
            color=discord.Color.orange()
        )
        return embed

    except Exception as e:
        # Return an error embed instead of a string
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        return embed
