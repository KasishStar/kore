"""
WebReflex — Lightweight web search via DuckDuckGo API.
No heavy dependencies, stays under 50KB.
"""

import requests


class WebReflex:
    def __init__(self):
        self.user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.api_url = "https://api.duckduckgo.com/"
        self.html_url = "https://html.duckduckgo.com/html/"

    def search(self, query, max_results=5):
        """Primary search method. Uses DDG Instant Answer API first, falls back to HTML."""
        results = self._search_api(query, max_results)
        if results and results[0].get("title") != "API Error":
            return results
        return self._search_html(query, max_results)

    def _search_api(self, query, max_results=5):
        """Search using DuckDuckGo Instant Answer API."""
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            }
            headers = {"User-Agent": self.user_agent}
            resp = requests.get(
                self.api_url, params=params, headers=headers, timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            results = []

            abstract = data.get("Abstract", "")
            if abstract:
                source = data.get("AbstractSource", "Unknown")
                results.append({
                    "title": f"Summary from {source}",
                    "snippet": abstract[:500],
                    "url": data.get("AbstractURL", ""),
                })

            answer = data.get("Answer", "")
            if answer and answer != abstract:
                results.append({
                    "title": "Answer",
                    "snippet": answer,
                    "url": "",
                })

            for topic in data.get("RelatedTopics", []):
                if "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", "")[:300],
                        "url": topic.get("FirstURL", ""),
                    })
                elif "Topics" in topic:
                    for sub in topic["Topics"][:2]:
                        results.append({
                            "title": sub.get("Text", "")[:100],
                            "snippet": sub.get("Text", "")[:300],
                            "url": sub.get("FirstURL", ""),
                        })
                if len(results) >= max_results:
                    break

            return results

        except Exception as e:
            return [{"title": "API Error", "snippet": f"Search failed: {e}", "url": ""}]

    def _search_html(self, query, max_results):
        """Fallback search using DDG HTML interface."""
        try:
            params = {"q": query}
            headers = {"User-Agent": self.user_agent}
            resp = requests.get(
                self.html_url, params=params, headers=headers, timeout=10
            )
            resp.raise_for_status()

            import re
            results = []

            # Try different HTML patterns
            patterns = [
                r'class="result__body".*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</',
                r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, resp.text, re.DOTALL)
                for match in matches[:max_results]:
                    if isinstance(match, tuple):
                        url = match[0]
                        title = re.sub(r"<[^>]+>", "", match[1]).strip()
                        snippet = match[2] if len(match) > 2 else ""
                        snippet = re.sub(r"<[^>]+>", "", snippet).strip()
                    else:
                        url = ""
                        title = re.sub(r"<[^>]+>", "", match).strip()
                        snippet = ""
                    if title:
                        results.append({
                            "title": title[:100],
                            "snippet": snippet[:300],
                            "url": url,
                        })
                if results:
                    break

            return results if results else [{"title": "No Results",
                                              "snippet": "Could not find information for that query.",
                                              "url": ""}]

        except Exception as e:
            return [{"title": "Search Error", "snippet": f"Search failed: {e}", "url": ""}]

    def fetch_url(self, url):
        """Fetch and extract readable text from a specific URL."""
        try:
            headers = {"User-Agent": self.user_agent}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            import re
            text = resp.text
            for tag in ["script", "style", "nav", "footer", "header", "noscript"]:
                text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            readable = [l for l in lines if len(l) > 40][:30]
            return "\n".join(readable) if readable else "No readable content found."
        except Exception as e:
            return f"Failed to fetch URL: {e}"

    def format_results(self, results):
        """Formats search results into a clean readable block."""
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}")
            if r['snippet']:
                lines.append(f"   {r['snippet']}")
            if r['url']:
                lines.append(f"   Source: {r['url']}")
            lines.append("")
        return "\n".join(lines) if results else "No results found."
