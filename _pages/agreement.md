---
layout: single
title: "소유주 인증/동의 안내"
permalink: /agreement/
---

{% assign privacy_consent_url = "https://www.buonestop.com/h/bs124/member-info-verification/intro" %}

# 📝 압도적 동의율로 재건축을 쟁취합시다

재건축 사업의 첫걸음은 **특별정비구역(선도지구) 지정**입니다. 이를 위해 소유주 여러분의 신속한 개인정보 동의와 재건축 전자 동의가 필요합니다.

---

## 📂 소유주 인증/동의 참여 프로세스 (2단계)

본 과정은 보안 및 개인정보 보호를 위해 **[1차 개인정보 동의]** 후 **[2차 재건축 전자 동의]** 단계로 진행됩니다.

### 1차 개인정보 동의
개인정보 보호법에 따라, 2차 재건축 전자 동의 링크 발송을 위해 먼저 진행하는 사전 동의입니다.
1.  아래의 **[1차 개인정보 동의 바로가기]** 버튼을 클릭하거나 안내문의 QR 코드를 스캔합니다.
2.  화면에서 **[본인 인증하기]**를 클릭합니다.
3.  성함, 생년월일 등 필수 정보를 순서대로 입력합니다.
4.  완료 화면이 나오면 정상적으로 접수된 것입니다.

<div style="text-align: center; margin: 2.5em 0;">
  <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 15px;">개인정보 동의 참여하기</p>
  <div style="margin-bottom: 20px;">
    <div id="privacy-consent-qr" data-url="{{ privacy_consent_url }}" aria-label="1차 개인정보 동의 QR 코드" style="display: inline-block; border: 1px solid #eee; padding: 10px; border-radius: 10px; background: #fff;"></div>
    <p style="font-size: 0.9rem; color: #666; margin-top: 5px;">스마트폰 카메라로 스캔하여 즉시 참여</p>
  </div>
  <a href="{{ privacy_consent_url }}" class="btn btn--primary btn--x-large" style="font-size: 1.25rem; padding: 1.5rem 3rem;">👉 1차 개인정보 동의 바로가기</a>
  <p style="margin-top: 15px;">
    <a href="{{ '/assets/raw_docs/전자서명동의서참여안내.pdf' | relative_url }}" class="btn btn--info" target="_blank">📋 상세 참여방법 가이드 보기 (PDF)</a>
  </p>
  <p style="margin-top: 10px; color: #888;">* KT Paperless 시스템을 통해 안전하게 진행됩니다.</p>
</div>

<script src="{{ '/assets/js/vendor/qrcode.min.js' | relative_url }}"></script>
<script>
  (function () {
    var target = document.getElementById("privacy-consent-qr");

    if (!target || !window.qrcode) {
      return;
    }

    var qr = window.qrcode(0, "M");
    qr.addData(target.getAttribute("data-url"));
    qr.make();
    target.innerHTML = qr.createSvgTag(4, 2);
  })();
</script>

### 2차 재건축 전자 동의
1차 개인정보 동의 완료 후, 시스템에서 소유주님의 휴대전화로 **개인별 고유 링크**가 포함된 문자를 발송합니다. (약간의 시간이 소요될 수 있습니다.)
1.  수신된 문자의 **링크를 클릭**하여 접속합니다.
2.  다시 한번 **[본인인증]**(문자 또는 PASS 앱)을 진행합니다.
3.  **[전체 동의]**를 클릭한 후 **[저장]**을 누릅니다.
4.  동의서 서식을 확인하신 후 **[전자동의서 서명하기]**를 클릭합니다.
5.  성함, **현재 거주 주소** 등을 입력하고 **정자로 이름을 기입**하여 서명을 완료합니다.
6.  최종 제출 후 '제출 완료' 문자까지 수신하시면 모든 절차가 끝납니다.

> **⚠️ 공동명의 소유주 주의사항:** 공동명의인 경우에는 **공동 소유주 모두가 동의**해주셔야 1세대 동의로 인정됩니다.

---

## ❓ 주요 유의사항 및 문의

*   **외부 소유주 주소 입력:** 실거주자가 아닌 경우, 인적사항 기입 시 **현재 실제 거주하고 계신 주소**를 입력해 주세요.
*   **보안 안내:** 민감한 개인정보 보호를 위해 1차 개인정보 동의 후 개인 맞춤형 2차 재건축 전자 동의 링크 방식으로 진행되오니 양해 부탁드립니다.
*   **기술 문의 (레디포스트 카카오톡):** 본인인증 실패, 공동명의 확인 등은 아래 링크로 문의해 주세요.

<div style="text-align: center; margin: 1.5em 0;">
  <a href="https://open.kakao.com/o/sYKyBhri" class="btn btn--info">💬 레디포스트 실시간 문의하기</a>
</div>

*   **전화 문의:** [010-4229-4805](tel:01042294805) / 레디포스트 [1833-5168](tel:18335168)

---
*본 전자 동의 시스템은 레디포스트(Readypost)에서 운영합니다.*
