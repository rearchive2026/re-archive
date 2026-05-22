# Re-archive-data (Private)

이 레포지토리는 재건축 원본 데이터와 가공 로직을 관리하는 **비공개 자산**입니다.

## 📁 구조
- `raw_data/`: 고시문, 원본 JSON 등 가공 전 데이터 (민감 정보 포함)
- `scripts/`: 데이터를 정제하고 공개용 파일을 생성하는 파이썬 스크립트
- `src/`: 추가 소스 코드 및 유틸리티
- `.github/workflows/`: GitHub Actions를 통한 자동 배포 설정

## 🔄 워크플로우
1. `raw_data/`에 새로운 데이터를 추가하거나 수정합니다.
2. 로컬에서 `python scripts/process.py`를 실행하여 결과를 확인합니다.
3. 변경 사항을 `main` 브랜치에 푸시하면 GitHub Actions가 실행됩니다.
4. 가공된 데이터가 [re-archive](https://github.com/rearchive2026/re-archive) (Public) 레포지토리로 자동 배포됩니다.

## 🔐 보안 주의사항
- **민감 데이터:** 필드명이 `_`로 시작하는 항목은 `process.py`에 의해 자동으로 마스킹됩니다.
- **PAT 설정:** `PUBLIC_REPO_TOKEN` 시크릿이 설정되어 있어야 자동 배포가 작동합니다.
