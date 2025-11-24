from django.core.management.base import BaseCommand
from accounts.models import College, Department

class Command(BaseCommand):
    help = "성신여대 단과대 및 학과 초기 데이터 생성"

    def handle(self, *args, **options):
        # 단과대 목록
        colleges = [
            ("간호대학", "NUR"),
            ("공과대학", "ENG"),
            ("미술대학", "ART"),
            ("법과대학", "LAW"),
            ("사범대학", "EDU"),
            ("사회과학대학", "SOC"),
            ("생활산업대학", "LIF"),
            ("음악대학", "MUS"),
            ("인문융합예술대학", "HUMA"),
            ("자연과학대학", "NAT"),
        ]

        # 학과 목록(단과대별)
        departments = [ 
            # 간호대학
            ("NUR", "간호학과", "NUR001"),

            # 공과대학
            ("ENG", "바이오생명공학과", "ENG001"),
            ("ENG", "바이오식품공학과", "ENG002"),
            ("ENG", "바이오신약의과학부", "ENG003"),
            ("ENG", "청정신소재공학과", "ENG004"), 
            ("ENG", "AI융합학부", "ENG005"),
            ("ENG", "서비스·디자인공학과", "ENG006"),      
            ("ENG", "융합보안공학과", "ENG007"),          
            ("ENG", "컴퓨터공학과", "ENG008"),                          

            # 미술대학
            ("ART", "공예과", "ART001"),
            ("ART", "동양화과", "ART002"),
            ("ART", "디자인과", "ART003"),
            ("ART", "서양화과", "ART004"),
            ("ART", "조소과", "ART005"),

            # 법과대학
            ("LAW", "법학부", "LAW001"),

            # 사범대학
            ("EDU", "교육학과", "EDU001"),
            ("EDU", "사회교육과", "EDU002"),
            ("EDU", "유아교육과", "EDU003"),
            ("EDU", "윤리교육과", "EDU004"),
            ("EDU", "한문교육과", "EDU005"),
            
            # 사회과학대학
            ("SOC", "경영학과", "SOC001"),
            ("SOC", "경제학과", "SOC002"),
            ("SOC", "미디어커뮤니케이션학과", "SOC003"),
            ("SOC", "사회복지학과", "SOC004"),
            ("SOC", "심리학과", "SOC005"),
            ("SOC", "정치외교학과", "SOC006"),
            ("SOC", "지리학과", "SOC007"),

            # 생활산업대학
            ("LIF", "뷰티산업학과", "LIF001"),
            ("LIF", "소비자산업학과", "LIF002"),
            ("LIF", "스포츠과학부", "LIF003"),
            ("LIF", "의류산업학과", "LIF004"),

            # 음악대학
            ("MUS", "기악과", "MUS001"),
            ("MUS", "성악과", "MUS002"),
            ("MUS", "작곡과", "MUS003"),

            # 인문융합예술대학
            ("HUMA", "국어국문학과", "HUMA001"),
            ("HUMA", "독일어문·문화학과", "HUMA002"),
            ("HUMA", "무용예술학과", "HUMA003"),
            ("HUMA", "문화예술경영학과", "HUMA004"),
            ("HUMA", "미디어영상연기학과", "HUMA005"),
            ("HUMA", "사학과", "HUMA006"),
            ("HUMA", "영어영문학과", "HUMA007"),
            ("HUMA", "일본어문·문화학과", "HUMA008"),
            ("HUMA", "중국어문·문화학과", "HUMA009"),
            ("HUMA", "프랑스어문·문화학과", "HUMA010"),
            ("HUMA", "현대실용음악학과", "HUMA011"), 

            # 자연과학대학
            ("NAT", "바이오헬스융합학부", "NAT001"),
            ("NAT", "수리통계데이터사이언스학부", "NAT002"),
            ("NAT", "화학·에너지융합학부", "NAT003"),
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("📌 단과대 생성 중..."))
        college_map = {} # 단과대 객체들 저장용 딕셔너리

        # 단과대 생성
        for college_name, college_code in colleges:
            #DB에 단과대 저장
            college, created = College.objects.get_or_create(
                college_id=college_code,
                defaults={"college_name": college_name},
            ) 
            college_map[college_code] = college #단과대 코드로 단과대 객체 저장

            # 생성 여부 출력
            if created:
                self.stdout.write(f" + 생성: {college_name} ({college_code})")
            else:
                self.stdout.write(f" - 이미 존재: {college_name} ({college_code})")

        self.stdout.write(self.style.MIGRATE_HEADING("📌 학과 생성 중..."))

        # 학과 생성
        for college_code, dept_name, dept_code in departments:
            college = college_map.get(college_code) #학과가 속할 단과대 찾기
            if not college: #단과대 코드가 잘못된 경우
                self.stdout.write(
                    self.style.WARNING(
                        f" ⚠ 단과대 코드 {college_code} 없음 → [{dept_name}] 건너뜀"
                    )
                )
                continue

            #DB에 학과 저장
            dept, created = Department.objects.get_or_create(
                dept_id=dept_code,
                defaults={
                    "dept_name": dept_name,
                    "college": college,
                },
            )
            if created:
                self.stdout.write(f" + 생성: {college.college_name} / {dept_name} ({dept_code})")
            else:
                # 이름/단과대 변경 시 업데이트
                updated = False
                if dept.dept_name != dept_name:
                    dept.dept_name = dept_name
                    updated = True
                if dept.college != college:
                    dept.college = college
                    updated = True
                if updated:
                    dept.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f" ✨ 업데이트: {college.college_name} / {dept_name} ({dept_code})"
                        )
                    )
                else:
                    self.stdout.write(
                        f" - 이미 존재: {college.college_name} / {dept_name} ({dept_code})"
                    )

        self.stdout.write(self.style.SUCCESS("\n🎉 단과대/학과 seed 작업 완료!"))


