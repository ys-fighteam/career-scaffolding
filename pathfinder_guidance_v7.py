"""PATHFINDER v7: learner-led examples, staged scaffolding, and trusted discovery links.

The 90 curated example cards are *draft teaching examples*, not verified job standards.
No live scraping, background requests, or third-party user data transfer occurs here.
"""
import json
import re
from pathlib import Path

LINKAREER_ACTIVITY_URL = 'https://linkareer.com/list/activity'
GUIDED_QIDS = {'Q03', 'Q04', 'Q05', 'Q07', 'Q09', 'Q10', 'Q13'}


def load_example_data():
    path = Path(__file__).with_name('pathfinder_examples_v6.json')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'cards': [], 'mapping_to_existing_db': {}}


_DATA = load_example_data()


def _fallback_examples(job, skill, task):
    """Provide six action-first *general* examples when a job has no curated cards."""
    simple = skill.split('›')[-1].strip() if '›' in skill else skill
    prefix = f'{job} 분야의 {simple}'
    return [
        {'id': 'generic-1', 'title': '핵심 개념 찾아보기',
         'action': f'{prefix}와 관련된 핵심 용어 3개를 찾아 내 말로 설명하기',
         'evidence': '용어 설명 카드 3개', 'estimated_effort': '30분'},
        {'id': 'generic-2', 'title': '실제 사례 살펴보기',
         'action': f'"{task}"와 연결되는 사례 2개를 찾고 공통점과 차이점 기록하기',
         'evidence': '사례 비교표 한 장', 'estimated_effort': '40분'},
        {'id': 'generic-3', 'title': '작은 모의 과제 해보기',
         'action': f'{simple}을 연습할 수 있는 간단한 가상 과제를 직접 수행하기',
         'evidence': '직접 작성한 결과물 1개', 'estimated_effort': '50분'},
        {'id': 'generic-4', 'title': '과정 점검하기',
         'action': f'{simple} 과제에서 잘된 점 2개와 어려운 점 1개를 기록하기',
         'evidence': '점검 메모 3개', 'estimated_effort': '20분'},
        {'id': 'generic-5', 'title': '피드백 받아 수정하기',
         'action': f'{simple} 결과물을 동료·선배에게 보여주고 의견 한 가지 반영하기',
         'evidence': '수정 전후 비교', 'estimated_effort': '40분'},
        {'id': 'generic-6', 'title': '다음 목표 설계하기',
         'action': f'{simple}을 다음에 적용할 상황 1개를 정하고 단계별 실행 방법 작성하기',
         'evidence': '다음 실행 계획 1쪽', 'estimated_effort': '30분'},
    ]


def examples_for(job, skill, task=''):
    mapping = _DATA.get('mapping_to_existing_db', {}).get(job, {})
    names = [human for human, originals in mapping.items() if skill in originals]
    if job == '마케팅·홍보' and '생성형 AI 활용' in skill and '생성형 AI 활용' not in names:
        names.append('생성형 AI 활용')
    cards = [item for item in _DATA.get('cards', [])
             if item.get('job') == job and item.get('skill') in names]
    if cards:
        return cards[:6], True
    return _fallback_examples(job, skill, task), False


def render_example_cards(st, state, config):
    job = state.get('job_title', '')
    skill = state.get('skill', '')
    task = config.get('jobs_db', {}).get(state.get('job_category',''), {}).get(job, {}).get('task', '')
    examples, curated = examples_for(job, skill, task)
    st.markdown('### 무엇부터 해볼까요?')
    st.caption('정답이나 필수 활동이 아닙니다. 나에게 맞는 활동을 골라 수정해 보세요.')
    label = '선택한 역량에 맞는 활동 예시 6개' if curated else '시작을 돕는 공통 활동 예시 6개'
    with st.expander(label, expanded=False):
        if not curated:
            st.caption('이 직무·역량의 전문가 검수 예시는 준비 중입니다. 아래는 범용 학습 활동의 예시입니다.')
        for i, e in enumerate(examples):
            st.markdown(f"**{i+1}. {e.get('title','활동')}**")
            st.write(e.get('action',''))
            st.caption(f"만들 결과물: {e.get('evidence','자기점검 기록')} · 예상 시간: {e.get('estimated_effort','직접 조정')}")
            if st.button('내 학습 활동 초안에 참고하기', key=f'guide_card_{job}_{skill}_{i}'):
                new = e.get('action','').strip()
                old = state.answers.get('Q09', '').strip()
                updated = f'{old}\n- {new}' if old else f'- {new}'
                state.answers['Q09'] = updated
                # Q09 is rendered after the example area: widget state is safe to set now.
                st.session_state['input_Q09'] = updated
                st.info('초안에 추가했어요. 그대로 따르기보다 본인의 시간·경험에 맞게 수정해 주세요.')
            st.divider()


def _needs_detail(answer):
    a = (answer or '').strip()
    if not a:
        return 'blank'
    if len(a) < 22 or any(x in a for x in ('잘하고 싶', '열심히', '꾸준히', '많이 배우', '그냥', '공부할 거', '모르겠')):
        return 'vague'
    return 'detailed'


def _simple_skill(skill):
    return (skill or '선택한 역량').split('›')[-1].strip()


def _features(answer):
    """Transparent rule-based checks; NOT objective skill measurement."""
    a = (answer or '').strip()
    return {
        'blank': not bool(a),
        'vague': len(a) < 22 or any(x in a for x in ('잘하고 싶', '열심히', '꾸준히', '많이 배우', '그냥', '공부할 거', '모르겠')),
        'action': any(x in a for x in ('비교', '분석', '작성', '만들', '정리', '기획', '실행', '제안', '연습', '측정', '설명', '발표', '검토', '개선', '구현', '찾', '조사', '피드백', '수집', '수행')),
        'result': any(x in a for x in ('비교표', '요약표', '표를', '표로', '차트', '도표', '보고서', '기획안', '초안', '결과물', '문서', '발표자료', '콘텐츠', '포트폴리오', '시안', '목록', '카드', '대시보드', '제안서', '기록', '파일', '메모')),
        'measure': bool(re.search(r'\d+\s*(?:개|건|회|쪽|명|분|시간|주|일|건수|%)|완료|체크리스트|검증|평가|피드백', a)),
        'time': bool(re.search(r'\d+\s*(?:주|일|시간|분|월)|(?:월|화|수|목|금|토|일)요일|(?:이번|다음)\s*주|매주|주차|오전|오후', a)),
    }


def make_scaffold(qid, answer, job, skill, stage=1, example=None, context=None):
    """Context-aware two-stage guiding questions, never a scored assessment."""
    context = context or {}
    a = (answer or '').strip()
    flags = _features(a)
    short = _simple_skill(skill)
    earlier = {
        'Q03': context.get('Q01'),
        'Q04': context.get('Q01'),
        'Q05': context.get('Q04'),
        'Q07': context.get('Q05'),
        'Q09': context.get('Q07'),
        'Q10': context.get('Q09'),
        'Q13': context.get('Q09') or context.get('Q07'),
    }.get(qid, '')
    ref = f" 앞에서 적은 '{str(earlier).strip()[:60]}' 내용을 떠올려 보세요." if earlier else ''

    if stage == 1:
        if qid == 'Q03':
            if flags['blank'] or flags['vague']:
                return f"{short} 역량과 연결되는 경험에서 **내가 직접 한 행동 한 가지**는 무엇인가요?{ref}"
            return '그 행동은 누구의 도움 없이 어디까지 수행할 수 있었나요? 실제 결과를 한 문장으로 적어 보세요.'
        if qid == 'Q04':
            return f"{short}와 관련해 지금 막히는 지점을 **시작·실행·검증** 중 어디라고 느끼나요?{ref}" if flags['vague'] else '직접 해본 과정 중 어느 순간에 멈췄는지, 그때 부족했던 자료나 방법을 떠올려 보세요.'
        if qid == 'Q05':
            return f"보완할 점이 여러 개라면 **4주 내에 연습 가능한 한 가지 행동**을 먼저 골라볼까요?{ref}"
        if qid == 'Q07':
            if not flags['action'] or flags['vague']:
                return f"4주 후 {short} 역량을 활용해 **어떤 행동을 직접 수행**하고 싶나요?{ref}"
            if not flags['result']:
                return '그 행동을 수행한 뒤 **보여줄 수 있는 결과물**은 무엇인가요? (표, 보고서, 기획안 등)'
            if not flags['measure']:
                return '목표를 달성했다는 것을 **무엇으로 확인**할 수 있나요? 횟수·개수·검토 기준 등을 생각해 보세요.'
            return '지금 정한 목표가 4주 안에 현실적으로 가능한가요? 시간이 부족하면 어느 부분을 줄일 수 있을까요?'
        if qid == 'Q09':
            if not flags['action'] or flags['vague']:
                return f"강의 듣기에서 끝나지 않도록, **직접 해볼 실습 행동**은 무엇인가요?{ref}"
            if not flags['result']:
                return '활동을 마친 뒤 어떤 기록이나 산출물이 남을까요?'
            return '이 활동은 앞에서 세운 목표에 어떻게 연결되나요? 필요한 선행 연습은 없나요?'
        if qid == 'Q10':
            if not flags['time']:
                return f"첫 활동을 **몇 주차, 무슨 요일**에 시작할 수 있나요?{ref}"
            if not flags['measure']:
                return '매번 몇 분 또는 몇 시간씩 실행할 수 있나요? 시험·과제 일정과 겹치지 않나요?'
            return '계획을 실행하지 못하는 주가 생긴다면, 최소한으로 유지할 활동은 무엇인가요?'
        if qid == 'Q13':
            return f"지금 20분만 쓸 수 있다면, 자료 찾기·도구 열기·첫 초안 중 **무엇부터 시작**하겠나요?{ref}"
        return '가장 작은 실행 행동 하나를 골라볼까요?'

    if example and qid in ('Q05','Q07','Q09'):
        return (f"예시: **{example.get('title', '작은 학습 활동')}** — "
                f"{example.get('action', '')} \n\n이 예시를 복사하지 말고 자신의 시간·경험에 맞게 어떻게 바꿀지 생각해 보세요.")
    second = {
        'Q03': f"{short}을 활용해 10분 안에 시도할 수 있는 활동을 한 가지 떠올리고, 어느 부분까지 혼자 해낼 수 있을지 적어보세요.",
        'Q04': '문제가 시작·실행·검증 중 한 단계에 있다면, 그 단계에서 필요한 도움이나 도구는 무엇인가요?',
        'Q05': '중요도와 실행 가능성, 두 가지 기준으로 어려움 한 가지를 비교해 본다면 무엇을 선택할까요?',
        'Q07': '예: 공개 자료 3건을 비교하고 결과를 한 쪽 표로 정리해, 내가 정한 2가지 기준으로 확인하기. 내 목표에서는 무엇을 바꾸면 좋을까요?',
        'Q09': '자료 1개 찾아보기 → 작은 결과물 만들기 → 스스로 체크하기, 이 중 이번 주에 할 한 활동은 무엇인가요?',
        'Q10': '예: 화·목요일 30분씩 조사, 토요일 40분씩 초안 수정. 내 실제 시간표에는 어떻게 배치할 수 있나요?',
        'Q13': '예: 오늘 15분 동안 자료 1개를 찾고 제목을 메모하기. 내 계획의 첫 행동은 무엇인가요?',
    }
    return second.get(qid, '원하는 결과물을 하나 정하고 가장 작은 실행 행동부터 적어보세요.')


def render_unified_help(st, state, config, qid, ai_callback=None):
    """Single guidance panel for default, staged and optional API AI help."""
    q = config.get('questions', {}).get(qid, {})
    guided = qid in GUIDED_QIDS
    job = state.get('job_title', '')
    skill = state.get('skill', '')
    answer = state.get('answers', {}).get(qid, '')
    task = config.get('jobs_db', {}).get(state.get('job_category', ''), {}).get(job, {}).get('task', '')

    with st.expander('도움받기 · 필요할 때만 펼쳐보세요', expanded=False):
        st.caption(q.get('default_hint', '직접 수행할 수 있는 작은 행동부터 생각해 보세요.'))
        if not guided:
            return

        import hashlib
        signature = hashlib.sha1(f'{job}::{skill}::{qid}'.encode('utf-8')).hexdigest()[:12]
        stage_key = f'ongil_hint_stage_{qid}_{signature}'
        ai_key = f'{qid}_{signature}'
        left, right = st.columns(2)
        with left:
            first_clicked = st.button('1차 · 질문 받기', key=f'ongil_first_{ai_key}', use_container_width=True)
        with right:
            second_clicked = st.button('2차 · 예시 보기', key=f'ongil_second_{ai_key}', use_container_width=True)
        if first_clicked:
            st.session_state[stage_key] = 1
        if second_clicked:
            st.session_state[stage_key] = 2
        stage = st.session_state.get(stage_key, 0)
        if stage:
            examples, _ = examples_for(job, skill, task)
            prompt = make_scaffold(qid, answer, job, skill, stage=stage,
                                   example=examples[0] if stage == 2 and examples else None,
                                   context=state.get('answers', {}))
            st.info(prompt)
            st.caption('규칙 기반 도움말입니다. 역량의 실제 수준을 판정한 결과가 아니며, 답을 복사할 필요도 없어요.')

        api_key = state.get('openai_api_key', '').strip()
        if ai_callback and q.get('ai_prompt'):
            st.divider()
            if api_key:
                st.caption('아래 버튼을 누를 때에만 현재 문항과 관련 이전 답변이 외부 AI API로 전송될 수 있습니다.')
                if st.button('AI 맞춤 질문 받기 (선택)', key=f'ongil_ai_{ai_key}', use_container_width=True):
                    with st.spinner('현재 작성한 내용에 맞춘 질문을 준비하고 있습니다...'):
                        reply = ai_callback(qid, job, skill, answer, api_key)
                    state.setdefault('ai_hints', {})[ai_key] = {'answer': answer, 'message': reply}
                cached = state.get('ai_hints', {}).get(ai_key)
                if isinstance(cached, dict):
                    if cached.get('answer') == answer:
                        st.info(cached.get('message', ''))
                    else:
                        st.caption('답변이 수정되어 이전 AI 힌트는 숨겼어요. 필요하면 다시 생성해 주세요.')
            else:
                st.caption('AI 질문은 선택 기능입니다. API Key가 없어도 1·2차 질문을 사용할 수 있습니다.')

        if stage or isinstance(state.get('ai_hints', {}).get(ai_key), dict):
            choice = st.radio('힌트 활용 방식', ['참고하여 내가 직접 수정하기', '내 답변 유지하기', '다른 관점으로 생각하기'],
                              key=f'ongil_hint_choice_{ai_key}')
            if choice == '다른 관점으로 생각하기':
                st.caption('예상보다 시간이 절반만 있다면 어느 활동을 먼저 남기겠나요?')
            elif choice == '참고하여 내가 직접 수정하기':
                st.caption('위 입력칸에서 내 말로 수정해 보세요. 자동으로 답변을 바꾸지는 않습니다.')


def render_stage_scaffold(st, state, config, qid):
    """Backward-compatible entry point; prefer render_unified_help."""
    return render_unified_help(st, state, config, qid)


def render_linkareer_panel(st, state, config):
    job=state.get('job_title','')
    skill=state.get('skill','')
    task=config.get('jobs_db', {}).get(state.get('job_category',''),{}).get(job,{}).get('task','')
    cards, _=examples_for(job,skill,task)
    words=[]
    for card in cards[:3]:
        words.extend(card.get('external_search_keywords',[]))
    if not words:
        words=[job,skill.split('›')[-1].strip()]
    words=list(dict.fromkeys(words))[:4]
    with st.expander('관련 대외활동·프로젝트 찾기 (선택)',expanded=False):
        st.write('다음 키워드로 링커리어에서 공고를 찾아 목표에 맞는지 확인해 보세요.')
        st.write(' · '.join(words))
        st.markdown(f'[링커리어 대외활동 목록 열기]({LINKAREER_ACTIVITY_URL})')
        st.caption('실시간 공고를 수집하거나 마감일을 검증한 추천은 아닙니다. 공고 원문에서 조건·일정·개인정보 요청을 확인해 주세요.')
        st.text_input('관심 있는 활동 링크를 기록해 두기 (선택)',key='saved_activity_url_v7',
                      placeholder='https://linkareer.com/...')
        st.text_area('이 활동이 나의 목표에 맞는 이유 (선택)',key='saved_activity_reason_v7',height=75)


def render_plan_summary_cards(st,state):
    a=state.get('answers',{})
    blocks=[('현재와 개선할 점','Q05'),('4주 목표·완료 기준','Q07'),
            ('학습 활동','Q09'),('일정','Q10')]
    columns=st.columns(2)
    for i,(title,qid) in enumerate(blocks):
        with columns[i%2]:
            with st.container(border=True):
                st.markdown(f'**{title}**')
                st.write(a.get(qid,'').strip() or '아직 작성하지 않았어요.')
    st.caption('위 내용은 자동 채점이 아니라 작성한 내용을 요약한 것입니다.')


def render_ethics_disclosure(st):
    st.info('이 서비스는 진로 적합성을 판정하지 않습니다. 제안·예시는 직접 검토하고 수정할 수 있습니다.')
    st.caption('실명·학번·연락처 등 개인정보를 입력하지 마세요. API Key를 통한 AI 기능은 외부 서비스로 학습 답변을 전송할 수 있으므로 사용 전 전송 내용을 확인하세요. 이 시연에서는 저장·보유·삭제 정책이 실제 서비스 운영 시 별도 확정되어야 합니다.')
