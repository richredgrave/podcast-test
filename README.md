# The Future in Tech

<img src="https://raybo.org/tfit-feed/images/artwork.jpg" width="250">

The [Future in Tech](https://go.raybo.org/tfit) is a weekly series powered by [LinkedIn Learning](https://www.linkedin.com/learning/) hosted by Senior Staff Instructor [Ray Villalobos](https://www.linkedin.com/in/planetoftheweb).

You can [watch it on LinkedIn](https://go.raybo.org/tfit-episodes) every Thursday at 2pm ET, 11am PT. The goal of this series is to spark conversations, provide practical tips and resources to help developers work, learn, and tackle challenges related to working in the technology industry.

We're talking about Generative AI tools like ChatGPT, Dall-E*2, Hugging Face by talking to some of the leaders delivering the tools, strategies and technologies that make working in technology exciting. We'll discuss how they broke into technology, business strategies, ethical concerns and technical skills.

You have a chance to hear from people who are not just talking about, but building the next generation tools like Open AI and leaders who've worked for and with Fortune 500 companies like Microsoft, Google, LinkedIn,  IBM,  Open AI and more.

---
## More Info
- [The Future in Tech Page](https://go.raybo.org/tfit)
- [Episode Guide](https://go.raybo.org/tfit-episodes)
- [YouTube Playlist](https://go.raybo.org/tfit-youtube)
- [Podcast Feed - Audio Only](https://go.raybo.org/tfit-feed-audio)
- [Episode Newsletter](https://go.raybo.org/tfit-newsletter)

---
## RSS Feed Generator

This repository includes an automated RSS 2.0 feed generator that reads [`feed.yaml`](feed.yaml) and publishes a podcast-directory–compatible `feed.xml` to GitHub Pages.

### How it works

1. **`feed.yaml`** — Single source of truth for the podcast and all episode metadata.
2. **`generate_feed.py`** — Python script that converts `feed.yaml` into a valid RSS 2.0 feed with Apple Podcasts / iTunes extensions.
3. **`.github/workflows/generate-feed.yml`** — GitHub Actions workflow that runs the generator on every push to `main` and deploys the output to GitHub Pages.

The live feed will be available at:
```
https://<owner>.github.io/<repo>/feed.xml
```

### Running the generator locally

```bash
pip install pyyaml
python generate_feed.py --base-url https://<owner>.github.io/<repo>
```

The generated `feed.xml` will appear in the repository root.

### Adding a new episode

Add a new entry under the `item` list in `feed.yaml`:

```yaml
item:
  - title: EP06-Your Episode Title
    description: A short summary of the episode.
    published: Thu, 16 Mar 2023 18:00:00 GMT
    file: /audio/TFIT06.mp3
    duration: "00:30:00"
    length: 43200000   # file size in bytes
```

Commit and push to `main`; the workflow will regenerate and redeploy `feed.xml` automatically.
