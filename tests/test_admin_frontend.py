import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AdminFrontendTests(unittest.TestCase):
    def run_node(self, source):
        result = subprocess.run(
            ["node", "-e", source],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip().splitlines()

    def test_browser_hash_and_qr_libraries_match_generated_data(self):
        source = textwrap.dedent(
            """
            const fs = require("fs");
            const vm = require("vm");

            const context = {
              console,
              document: {
                readyState: "complete",
                querySelector: () => null,
                addEventListener: () => {}
              }
            };
            context.window = context;
            vm.createContext(context);

            vm.runInContext(fs.readFileSync("assets/js/vendor/crypto-js.min.js", "utf8"), context);
            vm.runInContext(fs.readFileSync("assets/js/vendor/qrcode.min.js", "utf8"), context);
            vm.runInContext(fs.readFileSync("assets/js/verification-admin.js", "utf8"), context);

            const data = JSON.parse(fs.readFileSync("assets/data/verification-data.json", "utf8"));
            const identity = context.VerificationAdmin.normalizeIdentity("00101", "0301", "김 민준");
            const normalized = context.VerificationAdmin.normalizeRecord("00101", "0301", "김 민준", "4821");
            const wrongPhone = context.VerificationAdmin.normalizeRecord("00101", "0301", "김 민준", "0000");
            const identityHash = context.VerificationAdmin.sha256Hex(identity);
            const hash = context.VerificationAdmin.sha256Hex(normalized);
            const wrongPhoneHash = context.VerificationAdmin.sha256Hex(wrongPhone);
            const syntheticRecords = [
              {
                identityHash,
                hash,
                status: "대상",
                url: "https://sign.example.com/verify/topkn/101-301"
              },
              {
                identityHash: context.VerificationAdmin.sha256Hex("101|302|김민준"),
                status: "대상",
                url: "https://sign.example.com/verify/topkn/101-302",
                phoneMissing: true
              }
            ];
            const indexes = context.VerificationAdmin.buildRecordIndexes(syntheticRecords);
            const missingPhoneRecord = syntheticRecords[1];
            const targetPolicy = context.VerificationAdmin.getStatusPolicy("대상");
            const consentPolicy = context.VerificationAdmin.getStatusPolicy("개인정보동의필요");
            const holdPolicy = context.VerificationAdmin.getStatusPolicy("보류");
            const donePolicy = context.VerificationAdmin.getStatusPolicy("완료");
            const qr = context.qrcode(0, "M");
            qr.addData(syntheticRecords[0].url);
            qr.make();

            console.log(identity);
            console.log(normalized);
            console.log(hash === syntheticRecords[0].hash);
            console.log(identityHash === syntheticRecords[0].identityHash);
            console.log(indexes.fullHashMap.get(hash).url === syntheticRecords[0].url);
            console.log(indexes.fullHashMap.has(wrongPhoneHash) === false);
            console.log(indexes.identityHashMap.has(identityHash) === true);
            console.log(data.phoneMissingUrl === "https://www.naver.com");
            console.log(missingPhoneRecord.phoneMissing === true);
            console.log(missingPhoneRecord.hash === undefined);
            console.log(indexes.identityHashMap.has(missingPhoneRecord.identityHash) === true);
            console.log(indexes.fullHashMap.has(missingPhoneRecord.hash) === false);
            console.log(data.records.every((record) => record.identityHash && record.status && record.url));
            console.log(data.records.every((record) => record["이름"] === undefined && record["전화번호 뒷자리"] === undefined));
            console.log(targetPolicy.showQr === true);
            console.log(targetPolicy.message === "2차 재건축 전자 동의를 순서에 따라 작성해 주세요.");
            console.log(targetPolicy.statusLabel === "2차 재건축 전자 동의 필요");
            console.log(consentPolicy.showQr === true);
            console.log(consentPolicy.linkLabel === "1차 개인정보 동의 열기");
            console.log(consentPolicy.statusLabel === "1차 개인정보 동의 필요");
            console.log(holdPolicy.showQr === false);
            console.log(donePolicy.showQr === false);
            console.log(donePolicy.message === "2차 재건축 전자 동의 제출이 완료되었습니다.");
            console.log(donePolicy.statusLabel === "2차 재건축 전자 동의 완료");
            console.log(qr.createSvgTag(4, 2).includes("<svg"));
            """
        )

        self.assertEqual(
            self.run_node(source),
            [
                "101|301|김민준",
                "101|301|김민준|4821",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
                "true",
            ],
        )


if __name__ == "__main__":
    unittest.main()
