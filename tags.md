---
layout: page
title: Tags
permalink: /tags/
---

<h2>
  <i class="fas fa-tag"></i> Tags
</h2>

<ul class="page-tags">
  {% for tag in site.tags %}
    {% assign t = tag[0] | downcase %}
    <li>
      <a href="/tags/{{ tag[0] | slugify }}">
        {% if t == "hackthebox" %}
          <img src="/assets/icons/hackthebox.png" alt="Hack The Box Icon" class="inline-icon">
        {% elsif t == "tryhackme" %}
          <img src="/assets/icons/tryhackme.png" alt="TryHackMe Icon" class="inline-icon">
        {% elsif t == "wordpress" %}
          <img src="/assets/icons/wordpress.png" alt="WordPress Icon" class="inline-icon">
        {% elsif t == "linux" %}
          <img src="/assets/icons/linux.png" alt="Linux Icon" class="inline-icon">
        {% elsif t == "windows" %}
          <img src="/assets/icons/windows.png" alt="Windows Icon" class="inline-icon">
        {% elsif t contains "cve" %}
          <i class="fas fa-exclamation-triangle" style="color: #ffcc00;"></i>
        {% elsif t == "easy" %}
          <i class="fas fa-leaf" style="color: #28a745;"></i>
        {% elsif t == "medium" %}
          <i class="fas fa-circle" style="color: #ffc107;"></i>
        {% elsif t == "hard" %}
          <i class="fas fa-fire" style="color: #dc3545;"></i>
        {% elsif t == "insane" %}
          <i class="fas fa-skull-crossbones" style="color: #343a40;"></i>
        {% else %}
          <i class="fas fa-hashtag"></i>
        {% endif %}
        {{ tag[0] }} ({{ tag[1].size }})
      </a>
    </li>
  {% endfor %}
</ul>
