# PawShelf 웹사이트

macOS 앱 PawShelf의 소개 · 개인정보 처리방침 · 지원 페이지입니다. `https://archivelab-kr.github.io/pawshelf/`에서 GitHub Pages(main 브랜치 맨 위)로 공개됩니다.

- 문구는 `i18n/<언어>.json`(영어 `en.json`이 원본), 캐릭터 이름은 `i18n/characters.json`(앱 번역에서 가져옴)에 있습니다.
- `python3 build.py`가 언어별 `index.html` · `privacy.html` · `support.html`, 맨 위 `index.html`(브라우저 언어로 이동), `sitemap.xml`을 만듭니다. 만든 HTML은 손으로 고치지 않습니다. 모든 언어 파일이 영어와 같은 항목을 가졌는지 빌드할 때 검사합니다.
- `assets/demo/`: 실제 앱 녹화본(영상, 단계별 장면). 앱 저장소의 `scripts/record-demo.swift`, `scripts/cut-demo.swift`로 다시 만듭니다.
- `assets/chars/`: 캐릭터 그림. 앱 저장소의 `pawshelf-render`로 그린 `idle`(기본)과 `received`(`-hello`) 상태입니다.
- 언어별 첫 페이지에는 검색엔진용 앱 정보(JSON-LD `SoftwareApplication`)가 들어갑니다. 가격은 `build.py`의 `PRICE_USD`이고, App Store Connect 가격과 같게 둡니다.
- 출시 후 `build.py`의 `APP_STORE_URL`에 App Store 주소를 넣고 다시 빌드하면 "Coming soon"이 다운로드 버튼으로 바뀝니다.
- 외부 라이브러리 · 웹 글꼴 · 방문 통계를 쓰지 않습니다(외부 요청 0개).

```sh
python3 build.py
python3 -m http.server   # 로컬에서 열기
```
