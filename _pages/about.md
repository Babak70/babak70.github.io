---
permalink: /
title: "Babak Rahmani"
excerpt: "Efficient and agentic AI (reasoning, long-horizon generalization)"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

I’m Babak Rahmani, a Researcher at [Microsoft Research](https://www.microsoft.com/en-us/research/lab/microsoft-research-cambridge/) (Cambridge, UK) and a Visiting Researcher (sabbatical) at **BethgeLab** (Tübingen ELLIS & AI Center). My research sits at the intersection of **model architecture**, **efficient training/inference**, and **agentic systems**: making foundation models more reliable on long-horizon tasks (e.g., code generation/verification via execution state tracking) and more efficient through recurrent/implicit computation and systems-aware design. I work end-to-end—from problem framing and dataset/trace construction to large-scale training (7B-class; 200B+ token runs), evaluation, and post-training (alignment/RL)—with an engineering bias for reproducibility and clean interfaces. I did my PhD in Electrical Engineering at [EPFL](https://www.epfl.ch/en/) (Lausanne, Switzerland), supervised by [Christophe Moser](https://people.epfl.ch/christophe.moser?lang=en) and [Demetri Psaltis](https://scholar.google.com/citations?user=-CVR2h8AAAAJ&hl=en).

## News

* **Feb 2026**: Blog post: [Debugging CWMs: Where Traces Help (and Why They Fail)](https://babak70.github.io/code-world-models-blog/posts/state-tracking-code-world-models.html)
* **Sep 2025**: Joined **BethgeLab** (Tübingen ELLIS & AI Center) as a Visiting Researcher (sabbatical).
* **Sep 2025**: Two **Nature** papers (“AOC” and “Training Deep Physical Neural Networks”) published on the same day.
* **Apr 2025**: ASAP Seminar talk: “Implicit Language Models are RNNs” — [video](https://www.youtube.com/watch?v=F4HojFVEyd4), [paper](https://arxiv.org/abs/2502.07827), [slides](https://asap-seminar.github.io/assets/slides/asap_implicit_rnn.pdf)
* **2025**: **ICML Spotlight**: “Implicit Language Models are RNNs: Balancing Parallelization and Expressivity”.
* **2024**: Assistant Program Chair, **NeurIPS 2024**.
* **2023–2024**: Co-organizer, **NeurIPS** workshop **MLNCP** (Machine Learning with New Compute Paradigms).
* **2023**: Marie Skłodowska-Curie Fellowship (BiTFormer) — score **100/100** (≈ **9%** success rate).
* **Nov 2023**: “Backpropagation-free Training of Deep Physical Neural Networks” accepted to **Science**.
* **Sep 2022**: Paper accepted to **NeurIPS 2022**.
* **Jul 2022**: Started at Microsoft Research (Cambridge, UK).
* **Mar 2022**: PhD completed at EPFL.
* **Oct 2021**: Paper accepted to NeurIPS **ML4PhysicalSciences** workshop.
* **Jul 2020**: Paper accepted to **Nature Machine Intelligence**.
* **Dec 2019**: “Multimode optical fiber transmission with a deep learning network” recognized as a top-downloaded paper in **Nature Light: Science & Applications**.

## Selected publications
{% assign pubs = site.publications | sort: "date" | reverse %}

{% assign pub_order = "/publication/2026-02-16-learning-state-tracking-from-code-using-linear-rnns|/publication/2026-02-14-debugging-code-world-models|/publication/2025-09-01-training-deep-physical-neural-networks|/publication/2025-09-01-aoc|/publication/2025-02-01-implicit-language-models-rnns|/publication/2023-04-20-Backpropagation-free|/publication/2024-11-09-regularizing-the-infinite|/publication/2023-08-14-An-actor-model" | split: "|" %}

{% for permalink in pub_order %}
  {% assign post = site.publications | where: "permalink", permalink | first %}
  {% if post %}
    {% include archive-single.html type="list" show_read_more=false %}
  {% endif %}
{% endfor %}

{% for post in pubs %}
  {% unless pub_order contains post.permalink %}
    {% include archive-single.html type="list" show_read_more=false %}
  {% endunless %}
{% endfor %}



