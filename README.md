🎨 프론트엔드 (Frontend) 규칙
프론트엔드 파일(HTML, CSS, JS, 이미지)의 위치를 다음과 같이 정리합니다.

HTML 템플릿
템플릿 종류	위치	상세 규칙
개별 앱 템플릿	각 앱 폴더 안의 templates 폴더	각 기능에 특화된 HTML 파일들을 여기에 넣습니다.
기본 레이아웃	앱들과 같은 위치에 있는 templates 폴더	전체 페이지의 기본 구조를 담는 base.html 파일만 여기에 넣습니다.

Sheets로 내보내기
정적 파일 (Static Assets)
CSS, JavaScript, 이미지 파일은 static 폴더 내부에 종류별로 구분하여 넣습니다.

스타일 시트 (CSS): static/css/

자바스크립트 (JS): static/js/

이미지 (IMG): static/img/

⚙️ 백엔드 (Backend) 규칙
백엔드 로직과 관련된 파일 명명 규칙 및 기능 구현 위치를 정의합니다.

HTML 파일 명명 규칙
백엔드에서 사용하는 모든 HTML 파일은 이름 앞에 b_ 접두사를 붙여 프론트엔드 템플릿과 구분합니다.

잘못된 예시 (X)	올바른 예시 (O)
home.html	b_home.html
detail.html	b_detail.html

Sheets로 내보내기
기능 구현 위치
각 기능에 해당하는 로직(Views, Models 등)은 해당 앱 내부에서 작업해야 합니다. 이는 모듈성을 높이고 프로젝트 확장을 용이하게 하기 위함입니다.

규칙: 기능을 구현할 때는 항상 해당 앱 폴더 내부에서 작업합니다.
