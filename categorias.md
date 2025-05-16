---
layout: page
title: Categorías
permalink: /categories/
---

<h2>
  <i class="fas fa-folder"></i> Categorías
</h2>

<ul class="page-categories">
  {% for category in site.categories %}
    {% assign cat = category[0] | downcase %}
    <li>
      <a href="/categories/{{ category[0] | slugify }}">
        {% if cat == "hackthebox" %}
          <img src="/assets/icons/hackthebox.png" alt="Hack The Box Icon" class="inline-icon">
        {% elsif cat == "tryhackme" %}
          <img src="/assets/icons/tryhackme.png" alt="TryHackMe Icon" class="inline-icon">
        {% elsif cat == "wordpress" %}
          <img src="/assets/icons/wordpress.png" alt="WordPress Icon" class="inline-icon">
        {% elsif cat == "linux" %}
          <img src="/assets/icons/linux.png" alt="Linux Icon" class="inline-icon">
        {% elsif cat == "windows" %}
          <img src="/assets/icons/windows.png" alt="Windows Icon" class="inline-icon">
        {% elsif cat contains "cve" %}
          <i class="fas fa-exclamation-triangle" style="color: #ffcc00;"></i>
        {% elsif cat == "easy" %}
          <i class="fas fa-leaf" style="color: #28a745;"></i>
        {% elsif cat == "medium" %}
          <i class="fas fa-circle" style="color: #ffc107;"></i>
        {% elsif cat == "hard" %}
          <i class="fas fa-fire" style="color: #dc3545;"></i>
        {% elsif cat == "insane" %}
          <i class="fas fa-skull-crossbones" style="color: #343a40;"></i>
        {% else %}
          <i class="fas fa-folder-open"></i>
        {% endif %}
        {{ category[0] }} ({{ category[1].size }})
      </a>
    </li>
  {% endfor %}
</ul>
