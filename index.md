---
layout: splash
title: "탑마을 경남·벽산 통합 재건축 추진 준비 위원회"
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

{% assign briefing_notice_url = "/notices/2026/06/04/2차-특별정비구역-지정-최종-주민설명회-안내.html" | relative_url %}
{% assign briefing_notice_image = "/assets/images/재건축주민설명회.jpeg" | relative_url %}

<div
  id="briefing-notice-layer"
  class="briefing-notice-layer briefing-notice-layer--hidden"
  role="dialog"
  aria-modal="true"
  aria-labelledby="briefing-notice-title"
  data-notice-url="{{ briefing_notice_url }}"
>
  <div class="briefing-notice-dialog">
    <button type="button" class="briefing-notice-hitarea" aria-label="공지사항으로 이동">
      <span id="briefing-notice-title" class="screen-reader-text">2차 특별정비구역 지정을 위한 최종 주민설명회 안내</span>
      <img src="{{ briefing_notice_image }}" alt="2026 탑마을 경남·벽산 2차 특별정비구역 지정을 위한 최종 주민설명회 안내 포스터">
    </button>
    <div class="briefing-notice-actions">
      <label class="briefing-notice-checkbox">
        <input type="checkbox" id="briefing-notice-hide-today">
        <span>하루동안 닫기</span>
      </label>
      <button type="button" id="briefing-notice-close" class="btn btn--primary">닫기</button>
    </div>
  </div>
</div>

<style>
  .briefing-notice-layer {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
    background: rgba(0, 0, 0, 0.68);
  }

  .briefing-notice-layer--hidden {
    display: none;
  }

  .briefing-notice-dialog {
    width: min(595px, 100%);
    max-height: calc(100vh - 32px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  }

  .briefing-notice-hitarea {
    display: block;
    width: 100%;
    padding: 0;
    border: 0;
    background: transparent;
    cursor: pointer;
  }

  .briefing-notice-hitarea img {
    display: block;
    width: 100%;
    max-height: calc(100vh - 104px);
    object-fit: contain;
  }

  .briefing-notice-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    border-top: 1px solid #e5e5e5;
    background: #fff;
  }

  .briefing-notice-checkbox {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    color: #333;
    font-size: 0.95rem;
    cursor: pointer;
  }

  .briefing-notice-checkbox input {
    width: 18px;
    height: 18px;
    margin: 0;
  }

  #briefing-notice-close {
    margin: 0;
    white-space: nowrap;
  }

  @media (max-width: 480px) {
    .briefing-notice-layer {
      padding: 10px;
    }

    .briefing-notice-actions {
      padding: 10px;
    }

    .briefing-notice-checkbox {
      font-size: 0.9rem;
    }
  }
</style>

<script>
  (function () {
    var layer = document.getElementById("briefing-notice-layer");
    var closeButton = document.getElementById("briefing-notice-close");
    var hideToday = document.getElementById("briefing-notice-hide-today");
    var hitarea = layer ? layer.querySelector(".briefing-notice-hitarea") : null;
    var storageKey = "briefingNoticeHiddenDate";

    function todayKey() {
      var now = new Date();
      var year = now.getFullYear();
      var month = String(now.getMonth() + 1).padStart(2, "0");
      var day = String(now.getDate()).padStart(2, "0");
      return [year, month, day].join("-");
    }

    function getHiddenDate() {
      try {
        return window.localStorage.getItem(storageKey);
      } catch (error) {
        return null;
      }
    }

    function setHiddenDate() {
      try {
        window.localStorage.setItem(storageKey, todayKey());
      } catch (error) {
        return;
      }
    }

    function closeLayer() {
      if (hideToday && hideToday.checked) {
        setHiddenDate();
      }
      layer.classList.add("briefing-notice-layer--hidden");
    }

    function openNotice() {
      if (hideToday && hideToday.checked) {
        setHiddenDate();
      }
      window.location.href = layer.getAttribute("data-notice-url");
    }

    if (!layer || !closeButton || !hideToday || !hitarea) {
      return;
    }

    if (getHiddenDate() !== todayKey()) {
      layer.classList.remove("briefing-notice-layer--hidden");
    }

    closeButton.addEventListener("click", function (event) {
      event.stopPropagation();
      closeLayer();
    });

    hideToday.addEventListener("click", function (event) {
      event.stopPropagation();
    });

    hitarea.addEventListener("click", openNotice);
    layer.addEventListener("click", function (event) {
      if (event.target === layer) {
        openNotice();
      }
    });
  })();
</script>

{% include feature_row id="intro" type="center" %}

## 🏛️ 주요 업무 바로가기
{% include feature_row %}

## 📝 동의 참여 프로세스
[![동의 참여 프로세스]({{ '/assets/images/agreement-process.png' | relative_url }})]({{ '/agreement/' | relative_url }}){: .align-center style="max-width: 100%; height: auto;"}

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
