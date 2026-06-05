---
layout: single
title: "소유주 인증/동의"
permalink: /verification/
classes: wide
---

<style>
  .verification-shell {
    max-width: 720px;
    margin: 0 auto;
  }

  .verification-panel {
    border: 1px solid #d9dde3;
    border-radius: 8px;
    padding: 24px;
    background: #fff;
  }

  .verification-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .verification-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .verification-field label {
    font-weight: 700;
    font-size: 0.9rem;
  }

  .verification-field input {
    width: 100%;
    min-height: 44px;
    border: 1px solid #b8c0cc;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 1rem;
  }

  .verification-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .verification-actions .btn {
    margin: 0;
  }

  .verification-result {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #edf0f3;
    text-align: center;
  }

  .verification-result-status {
    display: inline-block;
    margin-bottom: 10px;
    border-radius: 999px;
    background: #eef3f8;
    color: #2d4059;
    padding: 6px 12px;
    font-size: 0.85rem;
    font-weight: 700;
  }

  .verification-result-message {
    margin: 0 0 18px;
    font-weight: 700;
    white-space: pre-line;
  }

  .verification-qr svg {
    width: min(260px, 100%);
    height: auto;
  }

  .verification-hidden {
    display: none !important;
  }

  @media (max-width: 640px) {
    .verification-panel {
      padding: 18px;
    }

    .verification-grid {
      grid-template-columns: 1fr;
    }

    .verification-actions {
      align-items: stretch;
      flex-direction: column;
    }
  }
</style>

<div class="verification-shell" data-verification-admin data-verification-data-url="{{ '/assets/data/verification-data.json' | relative_url }}">
  <section id="verification-owner-panel" class="verification-panel" aria-labelledby="verification-owner-title">
    <h2 id="verification-owner-title">소유주 정보 확인</h2>
    <form id="verification-owner-form" autocomplete="off">
      <div class="verification-grid">
        <div class="verification-field">
          <label for="verification-dong">동</label>
          <input id="verification-dong" name="dong" type="text" inputmode="numeric" autocomplete="off" required>
        </div>
        <div class="verification-field">
          <label for="verification-ho">호수</label>
          <input id="verification-ho" name="ho" type="text" inputmode="numeric" autocomplete="off" required>
        </div>
        <div class="verification-field">
          <label for="verification-name">이름</label>
          <input id="verification-name" name="name" type="text" autocomplete="off" required>
        </div>
        <div class="verification-field">
          <label for="verification-phone-last4">전화번호 뒷자리</label>
          <input id="verification-phone-last4" name="phone-last4" type="text" inputmode="numeric" pattern="[0-9]{1,4}" maxlength="4" autocomplete="off">
        </div>
      </div>
      <div class="verification-actions">
        <button class="btn btn--primary" type="submit">QR 확인하기</button>
      </div>
    </form>

    <div id="verification-result" class="verification-result verification-hidden" aria-live="polite">
      <div id="verification-result-status" class="verification-result-status"></div>
      <p id="verification-result-message" class="verification-result-message"></p>
      <div id="verification-qr" class="verification-qr"></div>
      <p>
        <a id="verification-link" class="btn btn--info">2차 재건축 전자 동의 열기</a>
      </p>
    </div>
  </section>
</div>

<script src="{{ '/assets/js/vendor/crypto-js.min.js' | relative_url }}"></script>
<script src="{{ '/assets/js/vendor/qrcode.min.js' | relative_url }}"></script>
<script src="{{ '/assets/js/verification-admin.js' | relative_url }}"></script>
