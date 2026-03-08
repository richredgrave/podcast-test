#!/usr/bin/env python3
"""
generate_feed.py — RSS 2.0 podcast feed generator.

Reads feed.yaml and writes a valid feed.xml file compatible with
Apple Podcasts, Spotify, and other podcast directories.

Usage:
    python generate_feed.py [--base-url URL] [--input feed.yaml] [--output feed.xml]

Environment variable:
    BASE_URL  — base URL of the site (e.g. https://richredgrave.github.io/podcast-test)
                Overridden by --base-url flag when provided.
"""

import argparse
import os
import sys
import yaml
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from xml.dom import minidom


def build_feed(data: dict, base_url: str) -> ET.Element:
    """Build an RSS 2.0 ElementTree from feed data."""

    base_url = base_url.rstrip("/")

    # Register namespaces so they appear as prefixes (not ns0, ns1…)
    ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")

    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
    })

    channel = ET.SubElement(rss, "channel")

    def sub(parent, tag, text=None, attrib=None):
        el = ET.SubElement(parent, tag, attrib or {})
        if text is not None:
            el.text = text
        return el

    # — Channel metadata —
    sub(channel, "title", data["title"])
    sub(channel, "link", base_url)
    sub(channel, "description", data["description"])
    sub(channel, "language", data.get("language", "en-us"))
    sub(channel, "generator", "generate_feed.py")
    sub(channel, "lastBuildDate", datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"))

    image_url = base_url + data["image"] if data["image"].startswith("/") else data["image"]
    image_el = sub(channel, "image")
    sub(image_el, "url", image_url)
    sub(image_el, "title", data["title"])
    sub(image_el, "link", base_url)

    # iTunes channel extensions
    sub(channel, "itunes:author", data.get("author", ""))
    sub(channel, "itunes:subtitle", data.get("subtitle", ""))
    sub(channel, "itunes:summary", data["description"])
    sub(channel, "itunes:explicit", "no")
    sub(channel, "itunes:image", attrib={"href": image_url})

    category = data.get("category", "Technology")
    sub(channel, "itunes:category", attrib={"text": category})

    # — Episodes —
    for item in data.get("item", []):
        entry = sub(channel, "item")

        sub(entry, "title", item["title"])
        sub(entry, "description", item["description"])
        sub(entry, "pubDate", item["published"])

        file_url = base_url + item["file"] if item["file"].startswith("/") else item["file"]
        sub(entry, "enclosure", attrib={
            "url": file_url,
            "length": str(item.get("length", 0)),
            "type": data.get("format", "audio/mpeg"),
        })

        # guid = file URL (permanent, not a page link)
        sub(entry, "guid", file_url)

        sub(entry, "itunes:title", item["title"])
        sub(entry, "itunes:summary", item["description"])
        sub(entry, "itunes:duration", str(item.get("duration", "")))
        sub(entry, "itunes:explicit", "no")

    return rss


def prettify(element: ET.Element) -> str:
    """Return an indented XML string for *element*."""
    raw = ET.tostring(element, encoding="unicode")
    reparsed = minidom.parseString(raw)
    return reparsed.toprettyxml(indent="  ", encoding=None)


def main():
    parser = argparse.ArgumentParser(description="Generate a podcast RSS feed from feed.yaml")
    parser.add_argument("--base-url", default=os.environ.get("BASE_URL", ""),
                        help="Base URL of the podcast site (e.g. https://example.github.io/podcast-test)")
    parser.add_argument("--input", default="feed.yaml", help="Path to feed.yaml (default: feed.yaml)")
    parser.add_argument("--output", default="feed.xml", help="Path for the generated feed.xml (default: feed.xml)")
    args = parser.parse_args()

    if not args.base_url:
        print("ERROR: --base-url is required (or set the BASE_URL environment variable).", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    rss = build_feed(data, args.base_url)
    xml_str = prettify(rss)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(xml_str)

    print(f"Feed written to {args.output}")


if __name__ == "__main__":
    main()
