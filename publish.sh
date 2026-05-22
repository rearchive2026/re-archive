#!/bin/bash

# 1. 로컬 환경 변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🚀 데이터 가공을 시작합니다..."
# 2. 로컬에서 AI 가공 실행
python3 scripts/process.py

if [ $? -ne 0 ]; then
    echo "❌ 가공 실패! 스크립트를 확인해 주세요."
    exit 1
fi

echo "✅ 가공 완료! GitHub으로 전송을 시작합니다..."

# 3. 비공개 레포 (re-archive-data) 푸시
git add .
git commit -m "Update data and site: $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main

# 4. 공개 레포 (re-archive) 푸시
cd ../re-archive
git add .
git commit -m "Deploy site: $(date +'%Y-%m-%d %H:%M:%S')"
git push origin main

echo "🎉 모든 배포가 완료되었습니다!"
echo "웹사이트 주소: https://rearchive2026.github.io/re-archive/"
