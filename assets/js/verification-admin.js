(function () {
  "use strict";

  var DATA_SELECTOR = "[data-verification-admin]";
  var HIDDEN_CLASS = "verification-hidden";
  var STATUS_POLICIES = {
    "대상": {
      showQr: true,
      message: "2차 재건축 전자 동의를 순서에 따라 작성해 주세요.",
      linkLabel: "2차 재건축 전자 동의 열기",
      statusLabel: "2차 재건축 전자 동의 필요",
    },
    "개인정보동의필요": {
      showQr: true,
      message:
        "1차 개인정보 동의가 필요합니다. 1차 개인정보 동의를 먼저 완료해 주세요.\n" +
        "1차 개인정보 동의가 이루어지면 약 5분 뒤 인증한 핸드폰으로 문자 발송되는 2차 재건축 전자 동의를 순서에 따라 작성 완료해 주세요.",
      linkLabel: "1차 개인정보 동의 열기",
      statusLabel: "1차 개인정보 동의 필요",
    },
    "보류": {
      showQr: false,
      message: "현재 확인이 필요한 상태입니다. 추진 준비 위원회에 문의해 주세요.",
    },
    "완료": {
      showQr: false,
      message: "2차 재건축 전자 동의 제출이 완료되었습니다.",
      statusLabel: "2차 재건축 전자 동의 완료",
    },
  };
  var DEFAULT_PHONE_MISSING_URL = "https://www.naver.com";
  var dataCache = null;

  function byId(id) {
    return document.getElementById(id);
  }

  function sha256Hex(value) {
    if (!window.CryptoJS || !window.CryptoJS.SHA256) {
      throw new Error("CryptoJS is not loaded.");
    }
    return window.CryptoJS.SHA256(value).toString();
  }

  function normalizeNumber(value) {
    var normalized = String(value || "").replace(/\s+/g, "").replace(/^0+/, "");
    return normalized || "0";
  }

  function normalizeName(value) {
    return String(value || "").trim().replace(/\s+/g, "");
  }

  function normalizePhoneLast4(value) {
    var digits = String(value || "").replace(/\D+/g, "");
    if (!digits || digits.length > 4) {
      return null;
    }
    return digits.padStart(4, "0");
  }

  function normalizeRecord(dong, ho, name, phoneLast4) {
    var identity = normalizeIdentity(dong, ho, name);

    if (!identity) {
      return null;
    }

    var normalizedPhone = normalizePhoneLast4(phoneLast4);
    if (!normalizedPhone) {
      return null;
    }

    return [identity, normalizedPhone].join("|");
  }

  function normalizeIdentity(dong, ho, name) {
    var normalizedName = normalizeName(name);

    if (!normalizedName) {
      return null;
    }

    return [normalizeNumber(dong), normalizeNumber(ho), normalizedName].join("|");
  }

  function buildRecordIndexes(records) {
    var fullHashMap = new Map();
    var identityHashMap = new Map();

    records.forEach(function (record) {
      if (record.hash) {
        fullHashMap.set(record.hash, record);
      }
      if (record.identityHash) {
        identityHashMap.set(record.identityHash, record);
      }
    });

    return {
      fullHashMap: fullHashMap,
      identityHashMap: identityHashMap,
    };
  }

  function setBusy(form, busy) {
    var button = form.querySelector("button[type='submit']");
    if (button) {
      button.disabled = busy;
    }
  }

  function show(element) {
    element.classList.remove(HIDDEN_CLASS);
  }

  function hide(element) {
    element.classList.add(HIDDEN_CLASS);
  }

  function loadData(root) {
    if (dataCache) {
      return Promise.resolve(dataCache);
    }

    var dataUrl = root.getAttribute("data-verification-data-url");
    return fetch(dataUrl, { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Verification data request failed.");
        }
        return response.json();
      })
      .then(function (data) {
        if (!data || !Array.isArray(data.records)) {
          throw new Error("Verification data is invalid.");
        }
        data.indexes = buildRecordIndexes(data.records);
        dataCache = data;
        return dataCache;
      });
  }

  function getStatusPolicy(status) {
    return STATUS_POLICIES[status] || {
      showQr: false,
      message: "현재 상태를 확인할 수 없습니다. 추진 준비 위원회에 문의해 주세요.",
    };
  }

  function renderQr(url, linkLabel) {
    var qrTarget = byId("verification-qr");
    var link = byId("verification-link");

    if (!window.qrcode) {
      throw new Error("QR library is not loaded.");
    }

    var qr = window.qrcode(0, "M");
    qr.addData(url);
    qr.make();

    qrTarget.innerHTML = qr.createSvgTag(6, 2);
    show(qrTarget);
    show(link);
    link.href = url;
    link.rel = "noopener noreferrer";
    link.target = "_blank";
    link.textContent = linkLabel || "2차 재건축 전자 동의 열기";
  }

  function renderResult(record) {
    var qrTarget = byId("verification-qr");
    var link = byId("verification-link");
    var message = byId("verification-result-message");
    var status = byId("verification-result-status");
    var policy = getStatusPolicy(record.status);

    message.textContent = policy.message;
    status.textContent = "상태: " + (policy.statusLabel || record.status);

    if (!policy.showQr) {
      hide(qrTarget);
      hide(link);
      show(byId("verification-result"));
      return;
    }

    renderQr(record.url, policy.linkLabel || "2차 재건축 전자 동의 열기");
    show(byId("verification-result"));
  }

  function renderPhoneMissingResult(data, record) {
    var message = byId("verification-result-message");
    var status = byId("verification-result-status");
    var url = data.phoneMissingUrl || DEFAULT_PHONE_MISSING_URL;

    message.textContent = "등록된 전화번호가 없어 별도 확인 QR로 안내합니다.";
    status.textContent = "상태: " + record.status + " / 전화번호 미등록";
    renderQr(url, "별도 확인 열기");
    show(byId("verification-result"));
  }

  function clearResult() {
    var qrTarget = byId("verification-qr");
    var link = byId("verification-link");

    qrTarget.innerHTML = "";
    show(qrTarget);
    show(link);
    byId("verification-result-message").textContent = "";
    byId("verification-result-status").textContent = "";
    link.removeAttribute("href");
    link.textContent = "2차 재건축 전자 동의 열기";
    hide(byId("verification-result"));
  }

  function bindOwnerForm(root) {
    var form = byId("verification-owner-form");

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      clearResult();
      setBusy(form, true);

      loadData(root)
        .then(function (data) {
          var hashInput = normalizeRecord(
            byId("verification-dong").value,
            byId("verification-ho").value,
            byId("verification-name").value,
            byId("verification-phone-last4").value
          );
          var identityInput = normalizeIdentity(
            byId("verification-dong").value,
            byId("verification-ho").value,
            byId("verification-name").value
          );

          if (!identityInput) {
            alert("해당 정보가 없습니다.");
            return;
          }

          if (hashInput) {
            var recordHash = sha256Hex(hashInput);
            var record = data.indexes.fullHashMap.get(recordHash);

            if (record) {
              renderResult(record);
              return;
            }
          }

          var identityHash = sha256Hex(identityInput);
          var identityRecord = data.indexes.identityHashMap.get(identityHash);
          if (identityRecord && identityRecord.phoneMissing) {
            renderPhoneMissingResult(data, identityRecord);
            return;
          }

          if (identityRecord) {
            alert("전화번호 뒷자리 확인이 필요합니다.");
            return;
          }

          alert("해당 정보가 없습니다.");
        })
        .catch(function () {
          alert("QR 코드를 생성하지 못했습니다.");
        })
        .finally(function () {
          setBusy(form, false);
        });
    });
  }

  function init() {
    var root = document.querySelector(DATA_SELECTOR);
    if (!root) {
      return;
    }

    bindOwnerForm(root);
    byId("verification-dong").focus();
  }

  window.VerificationAdmin = {
    normalizeNumber: normalizeNumber,
    normalizeName: normalizeName,
    normalizePhoneLast4: normalizePhoneLast4,
    normalizeIdentity: normalizeIdentity,
    normalizeRecord: normalizeRecord,
    buildRecordIndexes: buildRecordIndexes,
    getStatusPolicy: getStatusPolicy,
    renderPhoneMissingResult: renderPhoneMissingResult,
    sha256Hex: sha256Hex,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
