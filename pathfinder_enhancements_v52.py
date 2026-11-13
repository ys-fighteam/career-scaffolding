"""PATHFINDER v5.2 non-destructive additions for original Streamlit app.
Does not import third-party modules or contact the network.
"""
import html
from datetime import datetime

LEVEL_NAMES=(
  '가볍게 맛보기','차근차근 익히기','제법 잘해보기',
  '능숙하게 활용하기','완벽하게 마스터하기'
)
LEVEL_SHORT=('일단 찍먹','기본기 쌓기','제법 잘함','고수 모드','완전 정복')
LEVEL_DESCS=(
  '기초와 활동을 살펴보며 첫 시도를 해보기',
  '안내를 참고해 기본 절차를 연습하기',
  '익숙한 과제를 스스로 수행하고 결과를 확인하기',
  '새로운 상황에도 배운 방법을 적용하고 조정하기',
  '복잡한 과제도 독립적으로 수행하고 다른 사람에게 설명해보기',
)
CONTEXTS=(
 '수업·강의에서 이론이나 사례를 학습했어요',
 '과제·팀 프로젝트에서 직접 수행했어요',
 '동아리·대외활동에서 활용했어요',
 '인턴십·현장실습·업무에서 경험했어요',
 '개인 실습·자기주도 프로젝트를 진행했어요',
 '다른 사람의 작업을 관찰하거나 피드백했어요',
 '관련 경험이 아직 없어요','기타 경험',
)
ABILITY=(
 '아직 시도해 본 적이 없어요',
 '개념·목적 또는 절차를 설명할 수 있어요',
 '예시·자료를 보면서 시도할 수 있어요',
 '도움을 받으면 일부 또는 전체를 수행할 수 있어요',
 '익숙한 과제는 혼자 수행하고 결과를 확인할 수 있어요',
 '새로운 상황에서도 스스로 적용·조정할 수 있어요',
 '나의 접근 방식을 설명하고 다른 사람에게 피드백할 수 있어요',
 '현재 수준을 판단할 근거가 부족해요',
)
SUPPORTS=(
 '무엇부터 시작할지에 대한 안내','학습할 자료·도구','직접 연습할 기회',
 '결과를 점검할 기준·피드백','멘토·동료와의 의견 교류','실행 시간·일정 관리',
 '추가 지원이 필요하지 않아요','기타',
)

def goal_key(state):
 return f"{state.get('job_category','')}::{state.get('job_title','')}::{state.get('skill','')}"

def get_goal_level(state):
 v=state.get('goal_levels_v52',{}).get(goal_key(state),3)
 try:return max(1,min(5,int(v)))
 except (TypeError,ValueError):return 3

def render_goal_level(st,state):
 key=goal_key(state)
 levels=state.setdefault('goal_levels_v52',{})
 current=get_goal_level(state)
 st.markdown('### 🎯 나의 목표 레벨')
 st.caption('선택한 역량에 대해 이번 4주 동안 도전할 목표 수준을 선택해 보세요.')
 choice=st.radio('목표 레벨 선택',options=[1,2,3,4,5],index=current-1,
    horizontal=True,format_func=lambda x:f'LEVEL {x}',key='goal_radio_v52_'+key)
 levels[key]=int(choice)
 current=int(choice)
 # Screenshot-inspired segmented bar; native radio above provides keyboard-accessible control.
 segments=''.join(f'<div style="flex:1;min-width:0;text-align:center"><div style="height:12px;border-radius:12px;background:{"#7f8df4" if i<=current else "#eceef1"};margin-bottom:9px"></div><span style="font-size:11px;color:{"#273b57" if i==current else "#697586"};font-weight:{800 if i==current else 400}">{html.escape(LEVEL_SHORT[i-1])}</span></div>' for i in range(1,6))
 st.markdown(f'<div style="padding:15px;border:1px solid #e2e7ef;border-radius:14px;margin:8px 0 12px"><div style="display:flex;justify-content:space-between;margin-bottom:12px"><b>나의 목표 레벨</b><strong>Lv.{current}/5</strong></div><div style="display:flex;gap:5px">{segments}</div></div>',unsafe_allow_html=True)
 st.caption(f'**LEVEL {current} · {LEVEL_NAMES[current-1]}** — {LEVEL_DESCS[current-1]}')
 state.setdefault('goal_descriptions_v52',{})[key]=st.text_area(
   '목표에 도달하면 어떤 행동이나 결과물을 만들어 보고 싶나요? (선택)',
   value=state.setdefault('goal_descriptions_v52',{}).get(key,''),
   key='goal_behavior_v52_'+key,height=85,
   placeholder='예: 캠페인 데이터를 비교하고 개선 방향을 스스로 설명할 수 있다.'
 )
 st.caption("🛡️ 이 레벨은 학습자 본인이 선택한 도전 목표입니다. 실제 능력 인증이나 채용 기준이 아닙니다. ‘마스터’도 장기적인 지향을 나타내는 이름입니다.")

def render_experience_review(st,state):
 st.divider()
 st.markdown('### 🌱 나의 역량 경험 점검')
 st.caption('학습 계획을 완성했어요. 선택한 역량의 경험을 돌아보세요. 필수 2문항만 작성해도 충분해요.')
 st.markdown('**1. 이 역량을 어떤 방식으로 경험했나요?** (필수 · 복수 선택)')
 ctx=st.multiselect('경험 유형',CONTEXTS,key='v52_ref_contexts')
 if '관련 경험이 아직 없어요' in ctx and len(ctx)>1:
  st.warning('경험 없음과 다른 경험 유형을 동시에 선택하지 않도록 확인해 주세요.')
 st.markdown('**2. 현재 어느 정도 혼자 수행할 수 있나요?** (필수 · 하나 선택)')
 lv=st.radio('현재 수행 수준',ABILITY,index=None,key='v52_ref_level',label_visibility='collapsed')
 with st.expander('선택 문항 더 작성하기 · 판단 근거 / 필요한 지원 / 다음 행동'):
  evidence=st.text_area('3. 현재 수준을 판단한 근거 (선택)',key='v52_ref_evidence')
  support=st.multiselect('4. 추가로 필요한 지원 (선택)',SUPPORTS,key='v52_ref_support')
  action=st.text_area('5. 다음에 시도할 작은 행동 (선택)',key='v52_ref_action')
 state['experience_reflection_v52']={
   'skill':state.get('skill',''),'contexts':list(ctx),'level':lv or '',
   'evidence':evidence,'supports':list(support),'nextStep':action
 }
 done=bool(ctx and lv and not ('관련 경험이 아직 없어요' in ctx and len(ctx)>1))
 if done:st.success('필수 2문항을 완료했어요. 아래에서 계획을 저장할 수 있어요.')
 else:st.info('경험 유형과 현재 수행 수준에 답하면 경험 점검을 마칠 수 있어요.')
 return done

def _esc(x):return html.escape(str(x or '미작성'))

def printable_html(state,config):
 a=state.get('answers',{});ind=state.get('ind_answers',{});ef=state.get('experience_reflection_v52',{})
 level=get_goal_level(state)
 rows=[('현재 역량/보완점',a.get('Q05','')),('학습 목표',a.get('Q07','')),
       ('학습 활동',a.get('Q09','')),('일정과 우선순위',a.get('Q10','')),
       ('참고 자료',a.get('Q11','')),('계획 조정',a.get('Q12','')),('첫 행동',a.get('Q13',''))]
 def tbl(rows):return '<table>'+''.join(f'<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>' for k,v in rows)+'</table>'
 r=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>PATHFINDER 학습 계획서</title>
<style>body{{max-width:800px;margin:30px auto;padding:0 18px;font-family:"Malgun Gothic",sans-serif;line-height:1.65;color:#24354a}}h1{{color:#223c66}}h2{{margin-top:26px;color:#294b66}}table{{border-collapse:collapse;width:100%;margin:10px 0 24px}}th,td{{border:1px solid #dae2e8;padding:11px;text-align:left;vertical-align:top;white-space:pre-wrap}}th{{width:29%;background:#f2f6fa}}@media print{{@page{{size:A4;margin:16mm}}body{{margin:0;padding:0}}.toolbar{{display:none}}}}</style>
</head><body><div class="toolbar"><button onclick="window.print()">인쇄 · PDF로 저장</button></div><h1>PATHFINDER 학습 계획서</h1>
<p>직무: {_esc(state.get('job_title',''))} / 첫 번째 역량: {_esc(state.get('skill',''))} / 목표: LEVEL {level} {_esc(LEVEL_NAMES[level-1])}</p><h2>나의 학습 계획</h2>{tbl(rows)}
{('<h2>선택형 다음 역량 계획 · '+_esc(state.get('ind_skill',''))+'</h2>'+tbl([(f.get('label',''),ind.get(f.get('id',''),'')) for f in config.get('assessment_fields',[])])) if state.get('ind_skill','') else ''}
<h2>캘린더 일정</h2>{tbl([(e.get('date',''), f"{e.get('title','')} ({e.get('minutes',0)}분)") for e in state.get('events',[])]) if state.get('events') else '<p>등록된 일정이 없습니다.</p>'}
<h2>역량 경험 점검</h2>{tbl([('경험 유형',', '.join(ef.get('contexts',[]))),('수행 수준',ef.get('level','')),('판단 근거',ef.get('evidence','')),('필요한 지원',', '.join(ef.get('supports',[]))),('다음 행동',ef.get('nextStep',''))])}
<p style="color:#6a7480;font-size:12px">개인 학습 계획용 문서입니다. 객관적 역량 평가나 직무 적합성 진단으로 해석하지 마세요.</p></body></html>'''
 return r

def additional_exports(st,state,config,reflection_done):
 st.divider()
 st.markdown('### 📄 계획서 추가 저장 형식')
 st.caption('JSON과 ICS 다운로드는 그대로 유지됩니다. PDF로 저장할 때는 HTML 파일을 열고 인쇄 메뉴에서 PDF 저장을 선택하세요.')
 from io import StringIO
 summary=printable_html(state,config)
 md=['# PATHFINDER 나의 학습 계획',f"- 직무: {state.get('job_title','')}",f"- 역량: {state.get('skill','')}",f"- 목표 레벨: {get_goal_level(state)}/5",'']
 for k,v in [('보완할 점',state.get('answers',{}).get('Q05','')),('학습 목표',state.get('answers',{}).get('Q07','')),('학습 활동',state.get('answers',{}).get('Q09','')),('일정',state.get('answers',{}).get('Q10',''))]:md.extend([f'## {k}',str(v),''])
 c1,c2=st.columns(2)
 with c1:st.download_button('🖨️ PDF 저장용 계획서(.html)',data=summary,file_name='pathfinder-print-plan.html',mime='text/html',use_container_width=True,disabled=not reflection_done)
 with c2:st.download_button('📝 읽기 쉬운 계획서(.md)',data='\n'.join(md),file_name='pathfinder-study-plan.md',mime='text/markdown',use_container_width=True,disabled=not reflection_done)
