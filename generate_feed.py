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


def add_xml_child_element(parent_element, tag_name, text_content=None, attributes=None):
    """Create and append a child XML element to *parent_element*.

    Returns the newly created child element.
    """
    xml_child_element = ET.SubElement(parent_element, tag_name, attributes or {})
    if text_content is not None:
        xml_child_element.text = text_content
    return xml_child_element


def build_rss_feed(podcast_config: dict, site_base_url: str) -> ET.Element:
    """Build an RSS 2.0 ElementTree from the podcast configuration dictionary.

    Returns the root ``<rss>`` Element ready to be serialised.
    """

    site_base_url = site_base_url.rstrip("/")

    # Register namespaces so they appear as human-readable prefixes
    ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")

    rss_root_element = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
    })

    channel_element = ET.SubElement(rss_root_element, "channel")

    # — Channel-level metadata —
    add_xml_child_element(channel_element, "title", podcast_config["title"])
    add_xml_child_element(channel_element, "link", site_base_url)
    add_xml_child_element(channel_element, "description", podcast_config["description"])
    add_xml_child_element(channel_element, "language", podcast_config.get("language", "en-us"))
    add_xml_child_element(channel_element, "generator", "generate_feed.py")
    add_xml_child_element(
        channel_element,
        "lastBuildDate",
        datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
    )

    raw_cover_image_path = podcast_config["cover_image"]
    cover_image_url = (
        site_base_url + raw_cover_image_path
        if raw_cover_image_path.startswith("/")
        else raw_cover_image_path
    )
    channel_image_element = add_xml_child_element(channel_element, "image")
    add_xml_child_element(channel_image_element, "url", cover_image_url)
    add_xml_child_element(channel_image_element, "title", podcast_config["title"])
    add_xml_child_element(channel_image_element, "link", site_base_url)

    # iTunes channel-level extensions
    add_xml_child_element(channel_element, "itunes:author", podcast_config.get("author", ""))
    add_xml_child_element(channel_element, "itunes:subtitle", podcast_config.get("subtitle", ""))
    add_xml_child_element(channel_element, "itunes:summary", podcast_config["description"])
    add_xml_child_element(channel_element, "itunes:explicit", "no")
    add_xml_child_element(channel_element, "itunes:image", attributes={"href": cover_image_url})

    podcast_category = podcast_config.get("category", "Technology")
    add_xml_child_element(channel_element, "itunes:category", attributes={"text": podcast_category})

    # — Episodes —
    for episode in podcast_config.get("episodes", []):
        episode_element = add_xml_child_element(channel_element, "item")

        add_xml_child_element(episode_element, "title", episode["title"])
        add_xml_child_element(episode_element, "description", episode["description"])
        add_xml_child_element(episode_element, "pubDate", episode["published"])

        raw_audio_file_path = episode["audio_file"]
        audio_file_url = (
            site_base_url + raw_audio_file_path
            if raw_audio_file_path.startswith("/")
            else raw_audio_file_path
        )
        add_xml_child_element(episode_element, "enclosure", attributes={
            "url": audio_file_url,
            "length": str(episode.get("file_size_bytes", 0)),
            "type": podcast_config.get("audio_format", "audio/mpeg"),
        })

        # Use the audio file URL as the globally unique identifier for the episode
        add_xml_child_element(episode_element, "guid", audio_file_url)

        add_xml_child_element(episode_element, "itunes:title", episode["title"])
        add_xml_child_element(episode_element, "itunes:summary", episode["description"])
        add_xml_child_element(episode_element, "itunes:duration", str(episode.get("duration", "")))
        add_xml_child_element(episode_element, "itunes:explicit", "no")

    return rss_root_element


def prettify_xml(rss_element: ET.Element) -> str:
    """Return a human-readable, indented XML string for *rss_element*.

    Blank lines introduced by ``toprettyxml`` are stripped so the output
    is compact while remaining human-readable.
    """
    raw_xml_string = ET.tostring(rss_element, encoding="unicode")
    parsed_xml_document = minidom.parseString(raw_xml_string)
    indented_xml_string = parsed_xml_document.toprettyxml(indent="  ", encoding=None)
    # toprettyxml inserts blank lines between elements; remove them
    return "\n".join(
        line for line in indented_xml_string.splitlines() if line.strip()
    )


def main():
    argument_parser = argparse.ArgumentParser(
        description="Generate a podcast RSS feed from feed.yaml"
    )
    argument_parser.add_argument(
        "--base-url",
        default=os.environ.get("BASE_URL", ""),
        help="Base URL of the podcast site (e.g. https://example.github.io/podcast-test)",
    )
    argument_parser.add_argument(
        "--input",
        default="feed.yaml",
        help="Path to feed.yaml (default: feed.yaml)",
    )
    argument_parser.add_argument(
        "--output",
        default="feed.xml",
        help="Path for the generated feed.xml (default: feed.xml)",
    )
    parsed_arguments = argument_parser.parse_args()

    if not parsed_arguments.base_url:
        print(
            "ERROR: --base-url is required (or set the BASE_URL environment variable).",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(parsed_arguments.input, "r", encoding="utf-8") as yaml_input_file:
        podcast_config = yaml.safe_load(yaml_input_file)

    rss_root_element = build_rss_feed(podcast_config, parsed_arguments.base_url)
    formatted_xml_output = prettify_xml(rss_root_element)

    with open(parsed_arguments.output, "w", encoding="utf-8") as xml_output_file:
        xml_output_file.write(formatted_xml_output)

    print(f"Feed written to {parsed_arguments.output}")


if __name__ == "__main__":
    main()
