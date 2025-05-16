---
layout: page
title: Archive
---

<section class="archive-section">
  {% if site.posts[0] %}
    {% capture currentyear %}{{ 'now' | date: "%Y" }}{% endcapture %}
    {% capture firstpostyear %}{{ site.posts[0].date | date: '%Y' }}{% endcapture %}
    
    <!-- Mostrar "This year's posts" solo si el primer post es del año actual -->
    {% if currentyear == firstpostyear %}
        <h3>This year's posts</h3>
    {% endif %}

    <div class="archive-list">
      {% assign current_year = '' %}
      {% for post in site.posts %}
        {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
        
        <!-- Solo mostrar el título de un año si no es el año actual, o si es el primer post de ese año -->
        {% if year != current_year %}
          {% if current_year != '' %}
            </ul> <!-- Cerrar la lista anterior -->
          {% endif %}
          
          <!-- Si el año no es el actual, mostrar el encabezado con el año -->
          {% if year != currentyear %}
            <h3>{{ year }}</h3>
          {% endif %}
          
          <ul> <!-- Iniciar nueva lista -->
        {% endif %}
        
        <li class="post-item">
          <time>{{ post.date | date:"%d %b" }} - </time>
          <a href="{{ post.url | prepend: site.baseurl | replace: '//', '/' }}">
            {% assign categories_downcase = post.categories | join: ' ' | downcase %}
            {% if categories_downcase contains "hackthebox" %}
              <img src="/assets/icons/hackthebox.png" alt="Hack The Box Icon" class="archive-icon">
            {% elsif categories_downcase contains "tryhackme" %}
              <img src="/assets/icons/tryhackme.png" alt="TryHackMe Icon" class="archive-icon">
            {% endif %}
            {{ post.title }}
          </a>
        </li>

        {% assign current_year = year %}
      {% endfor %}
      </ul> <!-- Cerrar la última lista -->
    </div>
  {% endif %}
</section>

