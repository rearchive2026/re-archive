---
layout: splash
title: "탑마을 경남·벽산 재건축 추진위원회"
permalink: /
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  overlay_image: /assets/images/통합재건축조감도.png
  actions:
    - label: "동의서 안내"
      url: "/agreement/"
    - label: "재건축 FAQ"
      url: "/FAQ/"
excerpt: "분당의 새로운 중심, 경남·벽산의 미래 가치를 함께 만듭니다.<br /><br /><br /><br /><br /><br /><br /><br />"

intro:
  - excerpt: '**📣 8월 법 개정 전, 지금이 가장 중요한 시기입니다.** &nbsp; 7월 동의서 제출이 사업의 성패를 가릅니다. 압도적 동의로 단지 가치를 지켜주세요.'

feature_row:
  - title: "📝 소유주 인증 & 동의"
    excerpt: "전자서명 동의서 제출 및 본인인증 안내."
    url: "/agreement/"
    btn_label: "동의서 안내 보기"
    btn_class: "btn--primary"
  - title: "❓ 재건축 FAQ"
    excerpt: "분담금, 시공사 등 자주 묻는 질문을 정리했습니다."
    url: "/FAQ/"
    btn_label: "FAQ 보기"
    btn_class: "btn--info"
  - title: "🏗️ 사업 비전"
    excerpt: "통합 재건축의 가치와 배치도를 확인해 보세요."
    url: "/project-value/"
    btn_label: "비전 확인"
    btn_class: "btn--info"

---

{% include feature_row id="intro" type="center" %}

## 🏛️ 주요 업무 바로가기
{% include feature_row %}

## 📝 동의 참여 프로세스
[![동의 참여 프로세스](/assets/images/agreement-process.png)](/agreement/){: .align-center style="max-width: 100%; height: auto;"}

<div class="grid__wrapper" style="display:grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">

<div>
<h2>📢 최근 공지사항</h2>
{% assign notices = site.posts | where_exp: "p", "p.categories contains 'Notices'" %}
{% if notices.size > 0 %}
<ul>
{% for post in notices limit:5 %}
<li><a href="{{ post.url | relative_url }}" style="text-decoration: none;">{{ post.title }}</a> <small style="color:#888;">{{ post.date | date: site.date_format }}</small></li>
{% endfor %}
</ul>
{% else %}
<p><em>등록된 공지가 없습니다.</em></p>
{% endif %}

<p>
  <a class="btn btn--info" href="/categories/#Notices">전체 공지 보기</a>
</p>
</div>

<div>
<h2>❓ 자주 묻는 질문</h2>
{% assign faqs = site.posts | where_exp: "p", "p.categories contains 'FAQ'" %}
{% if faqs.size > 0 %}
<ul>
{% for post in faqs limit:5 %}
<li><a href="{{ post.url | relative_url }}" style="text-decoration: none;">{{ post.title }}</a> <small style="color:#888;">{{ post.date | date: site.date_format }}</small></li>
{% endfor %}
</ul>
{% else %}
<p><em>등록된 FAQ가 없습니다.</em></p>
{% endif %}

<p><a class="btn btn--info" href="/FAQ/">전체 FAQ 보기</a></p>
</div>

</div>
