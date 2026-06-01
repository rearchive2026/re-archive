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
            const normalized = context.VerificationAdmin.normalizeRecord("00101", "0301", "김 민준", "4821");
            const hash = context.VerificationAdmin.sha256Hex(normalized);
            const targetPolicy = context.VerificationAdmin.getStatusPolicy("대상");
            const holdPolicy = context.VerificationAdmin.getStatusPolicy("보류");
            const donePolicy = context.VerificationAdmin.getStatusPolicy("완료");
            const qr = context.qrcode(0, "M");
            qr.addData(data.records[0].url);
            qr.make();

            console.log(normalized);
            console.log(hash === data.records[0].hash);
            console.log(data.records[0].status === "대상");
            console.log(targetPolicy.showQr === true);
            console.log(holdPolicy.showQr === false);
            console.log(donePolicy.showQr === false);
            console.log(qr.createSvgTag(4, 2).includes("<svg"));
            """
        )

        self.assertEqual(
            self.run_node(source),
            [
                "101|301|김민준|4821",
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
