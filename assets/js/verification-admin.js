(function () {
  "use strict";

  var DATA_SELECTOR = "[data-verification-admin]";
  var HIDDEN_CLASS = "verification-hidden";
  var STATUS_POLICIES = {
    "대상": {
      showQr: true,
      message: "소유주 정보가 확인되었습니다. 아래 QR 코드로 전자서명을 진행해 주세요.",
      linkLabel: "전자서명 열기",
    },
    "보류": {
      showQr: false,
      message: "현재 확인이 필요한 상태입니다. 추진 준비 위원회에 문의해 주세요.",
    },
    "완료": {
      showQr: false,
      message: "이미 전자서명 절차가 완료된 정보입니다.",
    },
  };
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
    var normalizedPhone = normalizePhoneLast4(phoneLast4);
    var normalizedName = normalizeName(name);

    if (!normalizedPhone || !normalizedName) {
      return null;
    }

    return [
      normalizeNumber(dong),
      normalizeNumber(ho),
      normalizedName,
      normalizedPhone,
    ].join("|");
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
        if (!data || !data.passwordHash || !Array.isArray(data.records)) {
          throw new Error("Verification data is invalid.");
        }
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

  function renderResult(record) {
    var qrTarget = byId("verification-qr");
    var link = byId("verification-link");
    var message = byId("verification-result-message");
    var status = byId("verification-result-status");
    var policy = getStatusPolicy(record.status);

    message.textContent = policy.message;
    status.textContent = "상태: " + record.status;

    if (!policy.showQr) {
      hide(qrTarget);
      hide(link);
      show(byId("verification-result"));
      return;
    }

    if (!window.qrcode) {
      throw new Error("QR library is not loaded.");
    }

    var qr = window.qrcode(0, "M");
    qr.addData(record.url);
    qr.make();

    qrTarget.innerHTML = qr.createSvgTag(6, 2);
    show(qrTarget);
    show(link);
    link.href = record.url;
    link.rel = "noopener noreferrer";
    link.target = "_blank";
    link.textContent = policy.linkLabel || "전자서명 열기";
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
    link.textContent = "전자서명 열기";
    hide(byId("verification-result"));
  }

  function bindPasswordForm(root) {
    var form = byId("verification-password-form");

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      setBusy(form, true);

      loadData(root)
        .then(function (data) {
          var password = byId("verification-admin-password").value.trim();
          if (!/^\d{10}$/.test(password) || sha256Hex(password) !== data.passwordHash) {
            alert("암호가 일치하지 않습니다.");
            return;
          }

          hide(byId("verification-password-panel"));
          show(byId("verification-owner-panel"));
          byId("verification-dong").focus();
        })
        .catch(function () {
          alert("인증 데이터를 불러오지 못했습니다.");
        })
        .finally(function () {
          setBusy(form, false);
        });
    });
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

          if (!hashInput) {
            alert("해당 정보가 없습니다.");
            return;
          }

          var recordHash = sha256Hex(hashInput);
          var record = data.records.find(function (item) {
            return item.hash === recordHash;
          });

          if (!record) {
            alert("해당 정보가 없습니다.");
            return;
          }

          renderResult(record);
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

    bindPasswordForm(root);
    bindOwnerForm(root);
  }

  window.VerificationAdmin = {
    normalizeNumber: normalizeNumber,
    normalizeName: normalizeName,
    normalizePhoneLast4: normalizePhoneLast4,
    normalizeRecord: normalizeRecord,
    getStatusPolicy: getStatusPolicy,
    sha256Hex: sha256Hex,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
