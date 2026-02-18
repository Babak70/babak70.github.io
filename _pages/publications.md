---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---


 You can also find my articles on [Google Scholar](https://scholar.google.com/citations?user=Q3DLZlEAAAAJ&hl=en)


{% include base_path %}
{% assign pubs = site.publications | sort: "date" | reverse %}
{% for post in pubs %}
  {% include archive-single.html type="list" %}
{% endfor %}
