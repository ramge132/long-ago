-- 누락된 변형어 일괄 추가 SQL
-- 사용법: PostgreSQL에서 실행

-- 시간이 지남 카드 (추정 ID 찾기 필요)
INSERT INTO story_card_variants (story_card_id, variant) 
SELECT id, '시간' FROM story_card WHERE keyword = '시간이 지남'
UNION ALL
SELECT id, '지나' FROM story_card WHERE keyword = '시간이 지남'  
UNION ALL
SELECT id, '지났' FROM story_card WHERE keyword = '시간이 지남'
UNION ALL  
SELECT id, '지날' FROM story_card WHERE keyword = '시간이 지남'
UNION ALL
SELECT id, '흘러' FROM story_card WHERE keyword = '시간이 지남'
UNION ALL
SELECT id, '지나가' FROM story_card WHERE keyword = '시간이 지남';

-- 떨어짐 카드
INSERT INTO story_card_variants (story_card_id, variant)
SELECT id, '떨어짐' FROM story_card WHERE keyword = '떨어짐'
UNION ALL
SELECT id, '떨어진' FROM story_card WHERE keyword = '떨어짐'
UNION ALL  
SELECT id, '떨어져' FROM story_card WHERE keyword = '떨어짐'
UNION ALL
SELECT id, '떨어졌' FROM story_card WHERE keyword = '떨어짐'
UNION ALL
SELECT id, '떨어질' FROM story_card WHERE keyword = '떨어짐'
UNION ALL
SELECT id, '떨어' FROM story_card WHERE keyword = '떨어짐'
UNION ALL
SELECT id, '추락' FROM story_card WHERE keyword = '떨어짐'
UNION ALL
SELECT id, '추락한' FROM story_card WHERE keyword = '떨어짐';

-- 중단/멈춤 카드  
INSERT INTO story_card_variants (story_card_id, variant)
SELECT id, '중단' FROM story_card WHERE keyword = '중단/멈춤'
UNION ALL
SELECT id, '멈춤' FROM story_card WHERE keyword = '중단/멈춤'
UNION ALL
SELECT id, '멈춘' FROM story_card WHERE keyword = '중단/멈춤' 
UNION ALL
SELECT id, '멈추' FROM story_card WHERE keyword = '중단/멈춤'
UNION ALL 
SELECT id, '멈췄' FROM story_card WHERE keyword = '중단/멈춤'
UNION ALL
SELECT id, '멈출' FROM story_card WHERE keyword = '중단/멈춤'
UNION ALL
SELECT id, '정지' FROM story_card WHERE keyword = '중단/멈춤'
UNION ALL  
SELECT id, '그만' FROM story_card WHERE keyword = '중단/멈춤';

-- 노화 카드
INSERT INTO story_card_variants (story_card_id, variant)  
SELECT id, '노화' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '늙음' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '늙은' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '늙어' FROM story_card WHERE keyword = '노화' 
UNION ALL
SELECT id, '늙었' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '늙을' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '늙게' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '늙' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '나이' FROM story_card WHERE keyword = '노화'
UNION ALL
SELECT id, '연세' FROM story_card WHERE keyword = '노화';

-- 굶주림 카드  
INSERT INTO story_card_variants (story_card_id, variant)
SELECT id, '굶주림' FROM story_card WHERE keyword = '굶주림'
UNION ALL 
SELECT id, '굶주린' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶주려' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶주리' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶주렸' FROM story_card WHERE keyword = '굶주림' 
UNION ALL
SELECT id, '굶주릴' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶은' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶음' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶었' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶을' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶긴' FROM story_card WHERE keyword = '굶주림'
UNION ALL  
SELECT id, '굶어' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶겨' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶주' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '굶' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '배고' FROM story_card WHERE keyword = '굶주림'
UNION ALL
SELECT id, '배고픈' FROM story_card WHERE keyword = '굶주림';

-- 빛남 카드
INSERT INTO story_card_variants (story_card_id, variant)
SELECT id, '빛남' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '빛난' FROM story_card WHERE keyword = '빛남'  
UNION ALL
SELECT id, '빛나' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '빛났' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '빛날' FROM story_card WHERE keyword = '빛남'
UNION ALL 
SELECT id, '빛내' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '빛' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '반짝' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '반짝이' FROM story_card WHERE keyword = '빛남'
UNION ALL
SELECT id, '번쩍' FROM story_card WHERE keyword = '빛남';

-- 순진함 카드
INSERT INTO story_card_variants (story_card_id, variant)
SELECT id, '순진함' FROM story_card WHERE keyword = '순진함'  
UNION ALL
SELECT id, '순진한' FROM story_card WHERE keyword = '순진함'
UNION ALL
SELECT id, '순진하' FROM story_card WHERE keyword = '순진함'
UNION ALL
SELECT id, '순진했' FROM story_card WHERE keyword = '순진함'
UNION ALL
SELECT id, '순진할' FROM story_card WHERE keyword = '순진함'
UNION ALL
SELECT id, '순진' FROM story_card WHERE keyword = '순진함'  
UNION ALL
SELECT id, '천진' FROM story_card WHERE keyword = '순진함'
UNION ALL
SELECT id, '천진한' FROM story_card WHERE keyword = '순진함'
UNION ALL  
SELECT id, '순수' FROM story_card WHERE keyword = '순진함'
UNION ALL
SELECT id, '순수한' FROM story_card WHERE keyword = '순진함';

-- 기본 변형어가 없는 카드들을 위한 기본 변형어 추가
INSERT INTO story_card_variants (story_card_id, variant)
SELECT id, keyword FROM story_card 
WHERE keyword IN ('사망', '배신', '계약', '폭발', '승리', '패배', '음모', '공연', '식사', '모험', '희생', '실패', '유혹', '의식', '고백', '짝사랑', '진화', '텔레파시', '멸망', '결투', '부활', '착각', '그리움')
AND id NOT IN (SELECT DISTINCT story_card_id FROM story_card_variants);

-- 중복 제거
DELETE FROM story_card_variants 
WHERE id IN (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY story_card_id, variant ORDER BY id) as rn
        FROM story_card_variants
    ) t WHERE rn > 1
);