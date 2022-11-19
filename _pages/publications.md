---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---


 You can also find my articles on [Google Scholar](https://scholar.google.com/citations?user=Q3DLZlEAAAAJ&hl=en)


{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
