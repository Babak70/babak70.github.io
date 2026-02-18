---
permalink: /
title: "Babak Rahmani"
excerpt: "Efficient and agentic AI (reasoning, memory, compositional generalization)"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

I’m Babak Rahmani. I’m a Researcher at [Microsoft Research](https://www.microsoft.com/en-us/research/lab/microsoft-research-cambridge/) (Cambridge, UK) and a Visiting Researcher (sabbatical) at the Tübingen ELLIS & AI Center.

My research focuses on **efficient and agentic AI**, particularly **reasoning**, **memory**, and **compositional generalization** in large language models. I have experience with large-scale training (up to 7B parameters), post-training, alignment, and reinforcement learning.

Previously, I completed my PhD in Electrical Engineering at [EPFL](https://www.epfl.ch/en/) (Lausanne, Switzerland), supervised by [Christophe Moser](https://people.epfl.ch/christophe.moser?lang=en) and [Demetri Psaltis](https://scholar.google.com/citations?user=-CVR2h8AAAAJ&hl=en).

## Selected publications

<div class="grid__wrapper">
{% assign pubs = site.publications | sort: "date" | reverse %}
{% for post in pubs limit: 6 %}
  {% include archive-single.html type="grid" %}
{% endfor %}
</div>

[See all publications](/publications/)

## News

* **2025–now**: Visiting Researcher (Sabbatical), Tübingen ELLIS & AI Center; Marie Skłodowska-Curie Fellow (BiTFormer)
* **2022–now**: Researcher, Microsoft Research (Cambridge, UK)
* **2022**: PhD completed, EPFL


