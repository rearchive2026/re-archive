---
layout: archive
title: "재건축 자주 묻는 질문 (FAQ)"
permalink: /FAQ/
author_profile: true
---

재건축 사업과 관련하여 주민 여러분께서 가장 궁금해하시는 핵심 현안들을 모았습니다. 아래 목록에서 궁금하신 내용을 선택하여 확인해 보세요.

---

{% assign faq_posts = site.posts | where: "categories", "FAQ" %}
{% for post in faq_posts %}
  {% include archive-single.html %}
{% endfor %}

---

[주의/면책 공지 (Disclaimer)]
본 자료는 주민 여러분의 이해를 돕기 위해 '탑마을 경남·벽산 재건축 추진위원회'가 작성한 요약 안내 자료입니다. 구체적인 사항은 추후 법적 절차 및 관리처분계획 등에 따라 결정됩니다.
