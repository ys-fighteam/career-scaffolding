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


def make_scaffold(qid, answer, job, skill, stage=1, example=None):
    state = _needs_detail(answer)
    special = {
        'Q03': ('관련 경험 중에서 내가 직접 수행한 일을 한 가지 떠올려 볼까요?',
                '수업 발표 준비, 문서 정리, 동아리 홍보처럼 작은 행동도 경험이에요.'),
        'Q04': ('지금 혼자 하기 어려운 작업은 어느 단계에서 막히나요?',
                '시작하기·기준 정하기·도구 쓰기·결과 확인 중 한 단계를 골라 보세요.'),
        'Q05': ('여러 어려움 중 이번 달에 우선 개선할 한 가지는 무엇인가요? 왜 그것일까요?',
                '가장 영향이 크고 이번 달 안에 연습할 수 있는 행동 하나를 고르세요.'),
        'Q07': ('4주 후 구체적으로 어떤 행동을 하고 어떤 결과물을 남기고 싶나요?',
                '행동 + 결과물 + 완료 여부를 확인할 기준을 한 문장으로 적어 보세요.'),
        'Q09': ('이번 주에 바로 시도할 수 있는 가장 작은 연습 활동은 무엇인가요?',
                '자료 찾기 → 직접 수행 → 결과 확인 중 한 가지를 먼저 택해 보세요.'),
        'Q10': ('이번 주 어느 요일에 몇 분 동안 첫 활동을 할 수 있을까요?',
                '주중 또는 주말 날짜·시작 시간·소요 시간을 정해 캘린더에 적어보세요.'),
        'Q13': ('지금 20분이 있다면 계획의 어떤 부분부터 시작할 수 있나요?',
                '준비해야 하는 자료 한 개를 찾거나, 연습을 10분만 해보는 것도 괜찮아요.'),
    }
    first, second = special.get(qid, ('어떤 행동을 직접 해볼 수 있을까요?', '한 가지 행동과 산출물을 정해 보세요.'))
    if stage == 1:
        if state == 'blank':
            return f'아직 작성 전이에요. **{skill}**에 대해 {first}'
        if state == 'vague':
            return f'지금 적어주신 「{answer.strip()[:35]}」에서 한 걸음 더 나아가 볼까요? {first}'
        if qid in ('Q07','Q09','Q10') and not re.search(r'\d|주|요일|월|결과|표|보고서|시안|산출물|작성|제출', answer):
            return f'방향은 보여요. 이제 완료 여부를 확인할 수 있게 구체화해 볼까요? {first}'
        return f'직접 고민한 내용이 있네요. 이번에는 {second}'
    if example and qid in ('Q05', 'Q07', 'Q09'):
        return (f'예를 들면 **{example.get("title", "작은 활동")}**처럼 '
                f'「{example.get("action", "")}」라는 활동이 있어요. '
                '이것을 그대로 복사하지 않고, 자신의 경험과 시간에 맞게 어떻게 바꿀 수 있을까요?')
    return second


def render_stage_scaffold(st, state, config, qid):
    if qid not in GUIDED_QIDS:
        return
    job = state.get('job_title','')
    skill = state.get('skill','')
    task = config.get('jobs_db', {}).get(state.get('job_category',''), {}).get(job, {}).get('task','')
    examples, _ = examples_for(job,skill,task)
    answer = state.get('answers', {}).get(qid,'')
    with st.expander('답변을 구체화하는 질문 받기',expanded=False):
        stage_key=f'guide_step_{qid}'
        stage=st.session_state.get(stage_key,0)
        a,b=st.columns(2)
        with a:
            if st.button('1차 질문',key=f'guide_first_{qid}'):
                stage=1
        with b:
            if st.button('2차: 구체적인 예시',key=f'guide_second_{qid}'):
                stage=2
        st.session_state[stage_key]=stage
        if stage:
            st.info(make_scaffold(qid,answer,job,skill,stage,examples[0] if stage==2 and examples else None))
            st.caption('현재 입력한 문장을 바탕으로 한 규칙 기반 힌트입니다. 생성형 AI의 검증된 진단이 아닙니다.')
            st.radio('이 피드백을 어떻게 할까요?',
                     ['참고해서 내가 직접 수정하기','내 답변 유지하기','다른 관점으로 생각하기'],
                     key=f'guide_choice_{qid}',horizontal=False)
            if st.session_state.get(f'guide_choice_{qid}')=='다른 관점으로 생각하기':
                st.write('내가 가진 시간과 자원이 절반이라면, 가장 먼저 남길 활동 한 가지는 무엇일까요?')


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
