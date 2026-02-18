---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

My full CV (PDF): [cv_19_12_2025.pdf](/files/cv_19_12_2025.pdf)

## Short bio

I hold a PhD in Electrical Engineering with a multidisciplinary background spanning machine learning, physics, and biological systems. My current work focuses on efficient and agentic AI—particularly reasoning, memory, and compositional generalization in large language models.

## Education

* **PhD, Electrical Engineering**, EPFL (Lausanne, Switzerland), **2018–2022**
  * Thesis: *Learning of physical systems: from inference to control*
  * Supervisors: Christophe Moser & Demetri Psaltis
* **MSc, Electrical Engineering**, Sharif University of Technology (Tehran, Iran), **2014–2016**
* **BSc, Electrical Engineering**, University of Tehran (Tehran, Iran), **2010–2014**

## Experience

* **Researcher**, Microsoft Research (Cambridge, UK), **2022–now**
  * Efficient AI for improved LLM reasoning and recall
  * Post-training and alignment, including reinforcement learning
* **Visiting Researcher (Sabbatical)**, Tübingen ELLIS & AI Center (Tübingen, Germany), **2025–now**
  * Agentic systems, world models, and open-ended reasoning

## Selected publications

<ul>
{% assign pubs = site.publications | sort: "date" | reverse %}
{% for post in pubs limit: 10 %}
  {% include archive-single-cv.html %}
{% endfor %}
</ul>

## Selected talks

<ul>
{% assign talks = site.talks | sort: "date" | reverse %}
{% for post in talks limit: 10 %}
  {% include archive-single-talk-cv.html %}
{% endfor %}
</ul>
  
  
