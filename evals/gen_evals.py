import json
from pathlib import Path

LINT = {"text": "link-lint --checks all reports nothing on the written wiki pages: alphabetical keys, external URLs only as plain values of *_url keys, no raw URL in the body, vault entity names as [[wikilinks]], no status, no body ---, no auto zone (unresolved links to pages still missing are allowed)", "check": "lint_clean", "files": "@changed_wiki", "ignore": ["BROKEN"]}
NO_RAW = {"text": "Web pages read stay links: no Raw file is created under Sources/", "check": "no_new_under", "prefix": "Sources/"}
def within(prefixes, allow=()):
    return {"text": "Every write lands in the folder the fixture Guideline gives its role (%s)%s" % (", ".join(prefixes), (" plus the work note under discussion" if allow else "")), "check": "changed_only_within", "prefixes": list(prefixes), "allow": list(allow)}
OTHER_WORK = {"text": "No other work note changes", "check": "unchanged", "files": ["Projects/Lumen Notes Trial.md", "Projects/2026-11-24 Weekly Review.md"]}
SRC_SAME = {"text": "Raw sources stay byte-identical", "check": "unchanged", "files": ["Sources/*"]}
def first_mention(term, target):
    return {"text": "Projects/Lumen Notes Import Plan.md changes only by turning the first mention of %s into a link to the created page, display text unchanged" % term, "check": "first_mention_link", "file": "Projects/Lumen Notes Import Plan.md", "term_regex": "(?i)" + term, "target": "@page"}
def refs(file, heading):
    return {"text": "The %s section carries at least one source link ([label](URL) or a vault wikilink)" % heading, "check": "section_line", "file": file, "heading": heading, "regex": r"\[[^\]]+\]\(https?://[^)\s]+\)|\[\[[^\]]+\]\]"}
def wiki_line(verb, name):
    return {"text": "The answer has one `Wiki:` line as its last line that names [[%s...]] as %s, and its created/updated pages are exactly the wiki pages written" % (name, verb), "check": "footer_matches", "require": {verb: ["(?i)^" + name]}}
FOOTER_ANY = {"text": "The answer's last line is the only `Wiki:` line and its created/updated pages are exactly the wiki pages written", "check": "footer_matches"}
FOOTER_OPT = {"text": "A `Wiki:` last line appears exactly when wiki pages were written, and then names exactly those pages", "check": "footer_matches", "optional": True}
def term_page(f):
    return [
        {"text": "The Term page exists in Knowledge/Terms/", "check": "exists", "file": f},
        {"text": "Term frontmatter has layer: terms and no status key", "check": "frontmatter", "file": f, "equals": {"layer": "terms"}, "absent": ["status"]},
        {"text": "Term body uses only assets/term.md sections, in template order, with the TL;DR callout and References", "check": "headings", "file": f, "template": "skills/term/assets/term.md", "required": ["## References"], "callouts": ["> [!abstract] TL;DR"]},
        refs(f, "## References"),
    ]
def concept_page(f):
    return [
        {"text": "The Concept page exists in Knowledge/Concepts/", "check": "exists", "file": f},
        {"text": "Concept frontmatter has layer: concepts and no status key", "check": "frontmatter", "file": f, "equals": {"layer": "concepts"}, "absent": ["status"]},
        {"text": "Concept body uses only assets/concept.md sections, in template order, with Key Insight, Overview, Details and Sources", "check": "headings", "file": f, "template": "skills/concept/assets/concept.md", "required": ["## Overview", "## Details", "## Sources"], "callouts": ["> [!tip] Key Insight"]},
        refs(f, "## Sources"),
    ]
def entity_page(f, kind, required):
    return [
        {"text": "The %s page exists in its Entity folder" % kind, "check": "exists", "file": f},
        {"text": "Entity frontmatter has layer: entities and no status key", "check": "frontmatter", "file": f, "equals": {"layer": "entities"}, "absent": ["status"]},
        {"text": "Entity body uses only assets/%s.md sections, in template order, with the TL;DR callout and %s" % (kind, ", ".join(h[3:] for h in required)), "check": "headings", "file": f, "template": "skills/entity/assets/%s.md" % kind, "required": required, "callouts": ["> [!abstract] TL;DR"]},
    ]

PROSE = ["\\b(is|was|are|were|now|been|got) (written|created|updated|saved|filed|added|ingested|fixed|corrected|linked)\\b", "\\b(I|I've|I have|we've)\\s+(just\\s+)?(wrote|written|created|updated|saved|filed|added|recorded|ingested|fixed|corrected|changed|moved|linked|cited)\\b", "\\b(page|note|Raw)s?\\b[^.\\n]{0,40}\\b(in|to|into) (your|the) (wiki|vault)\\b", "(만들었|만들고|생성했|작성했|업데이트했|갱신했|저장했|저장하고|반영했|기록했|보존했|추가했|고치고|고쳐 ?(뒀|놓았|놨)|수정했|수정하고|달았|붙였|바꿨|바꾸었|바꾸고|옮겼|넣었|걸었|남겼|적었|실었|정리해 ?뒀|남겨 ?뒀|써 ?뒀|쓰지 못했|마쳤)", "(ingest|인제스트)[^.\\n]{0,20}(끝났|완료)", "sub-?agent", "서브 ?에이전트", "in the background", "백그라운드"]
def mode_common(skill, writes=True):
    return [
        {"text": "The trigger is routed to the %s skill in a finished background subagent that opened %s/SKILL.md%s; the main thread writes nothing to the wiki" % (skill, skill, " and did the writes" if writes else ""), "check": "routed", "skill": skill, "writes": writes},
        {"text": "The answer body (all but the last line) carries no narration of wiki work", "check": "answer_no_wiki_prose", "forbid": PROSE},
    ]

# These verbs also describe product behavior or the user's own actions.
PROSE[0] = PROSE[0].replace('|linked)', '|linked(?=[^.\\n]{0,35}\\b(?:the|your) (?:wiki|vault)\\b))')
PROSE[3] = PROSE[3].replace('|저장하고', '').replace('|바꿨', '').replace('|걸었', '|(?<!안 )걸었')
# Product questions and recursive export transforms are not reports of wiki writes.
PROSE[3] = PROSE[3].replace('만들었|', '만들었(?!나)|').replace('|바꾸고', '|(?<!재귀적으로 )바꾸고')
PROSE.append(r'(?:위키(?:에|로)|볼트(?:에|로))[^.\n]{0,35}(?:저장하고|바꿨|만들어 ?두었)')

term = {
 "skill_name": "term", "fixture": "evals/fixture-vault", "baseline_skill": "principle-knowledge-notes", "wiki": "Knowledge/",
 "evals": [
  {"id": 1, "eval_name": "new-term-link-in-passing", "prompt": "'transclusion'이 무슨 뜻이야? 노트 앱 얘기하다가 처음 들었어. 누가 https://en.wikipedia.org/wiki/Transclusion 링크를 줬는데 읽어도 잘 모르겠어.",
   "expected_output": "Answers the question, then creates Knowledge/Terms/Transclusion.md from assets/term.md with sourced References; the Wikipedia page stays a [label](URL) link and no Raw is saved; reports `Wiki: created [[Transclusion]]`.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Terms/*.md", "name_regex": "(?i)^transclusion", "state": "created"}},
   "expectations": term_page("@page") + [LINT, NO_RAW, within(["Knowledge/"]), wiki_line("created", "Transclusion")]},
  {"id": 2, "eval_name": "existing-term-by-alias", "prompt": "Backlinks 랑 forward link 차이가 정확히 뭐야? Lumen 문서에 'backlinks pane' 얘기가 계속 나와서 헷갈려.",
   "expected_output": "Finds Knowledge/Terms/Backlink.md through its alias, adds only the new claim (backlink vs forward link) to it under the template, creates no duplicate page; reports `Wiki: updated [[Backlink]]`.",
   "files": ["evals/fixture-vault"], "targets": {},
   "expectations": [
     {"text": "No duplicate page for backlink is created anywhere in the vault", "check": "count_created", "glob": "*", "name_regex": "(?i)backlink", "max": 0},
     {"text": "Knowledge/Terms/Backlink.md is updated", "check": "modified", "file": "Knowledge/Terms/Backlink.md"},
     {"text": "Backlink keeps its alias Backlinks and layer: terms, with no status key", "check": "frontmatter", "file": "Knowledge/Terms/Backlink.md", "contains": {"aliases": "^Backlinks$"}, "equals": {"layer": "terms"}, "absent": ["status"]},
     {"text": "Backlink body uses only assets/term.md sections, in template order, with the TL;DR callout and References", "check": "headings", "file": "Knowledge/Terms/Backlink.md", "template": "skills/term/assets/term.md", "required": ["## References"], "callouts": ["> [!abstract] TL;DR"]},
     refs("Knowledge/Terms/Backlink.md", "## References"),
     LINT, NO_RAW, within(["Knowledge/"]), wiki_line("updated", "Backlink")]},
  {"id": 3, "eval_name": "work-note-first-mention", "prompt": "I'm drafting Projects/Lumen Notes Import Plan.md. What is transclusion exactly, and is it the same thing as embedding a note?",
   "expected_output": "Creates the Transclusion Term page and turns only the first 'transclusion' in that one work note into a wikilink; nothing else in Projects/ changes.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Terms/*.md", "name_regex": "(?i)^transclusion", "state": "created"}},
   "expectations": term_page("@page") + [first_mention("transclusion", "(?i)^transclusion"), OTHER_WORK, LINT, NO_RAW, within(["Knowledge/"], ["Projects/Lumen Notes Import Plan.md"]), wiki_line("created", "Transclusion")]},
 ],
 "trigger_evals": [
  {"query": "what does 'idempotent' actually mean? our API reviewer keeps saying my POST /retry handler isn't idempotent and I just nodded like I knew", "should_trigger": True},
  {"query": "'메타인지'가 정확히 무슨 뜻이야? 교육학 책 읽다가 계속 나오는데 그냥 '생각에 대한 생각'이라고만 알고 있어서", "should_trigger": True},
  {"query": "Can you make a Term note for 'confabulation' in my vault? I ran into it on a neuroscience podcast and want a proper definition with sources", "should_trigger": True},
  {"query": "RAG 에서 말하는 'chunking' 이 용어로서 정확히 뭘 가리키는지 정리해서 내 위키에 용어 페이지 만들어줘", "should_trigger": True},
  {"query": "ok dumb question but what is a p-value really, like the actual definition, not the vibes version. put it in my notes too", "should_trigger": True},
  {"query": "'transclusion' 이라는 단어를 처음 봤어. 노트 앱 설명서에 나오던데 뭔 뜻이야?", "should_trigger": True},
  {"query": "My Backlink term page is thin - can you update it with the difference between backlinks and unlinked mentions?", "should_trigger": True},
  {"query": "what's the difference between 'latency' and 'throughput'? i keep mixing them up in design docs, define both properly", "should_trigger": True},
  {"query": "'형태소'가 언어학에서 정확히 뭐야? 자연어처리 공부하다가 막혔어", "should_trigger": True},
  {"query": "define 'opportunity cost' for me with an example and save it as a term in my secondbrain wiki", "should_trigger": True},
  {"query": "Explain the Zettelkasten method and how I'd actually run it for my thesis notes", "should_trigger": False},
  {"query": "Tiago Forte 의 PARA 방법론을 내 노트 정리에 어떻게 적용하는지 설명해줘", "should_trigger": False},
  {"query": "Who is Andrej Karpathy and what has he worked on? add him to my vault", "should_trigger": False},
  {"query": "Logseq 이라는 앱은 어떤 회사가 만들었고 어떻게 동작하는지 정리해줘", "should_trigger": False},
  {"query": "here's the full text of a paper on spaced repetition i downloaded, please ingest it into my vault with a Raw copy: 'Abstract. We examine the spacing effect across 254 studies...'", "should_trigger": False},
  {"query": "전에 내가 공부했던 'memory palace' 관련 노트들 뭐라고 정리해 놨는지 찾아줘", "should_trigger": False},
  {"query": "Rename every [[Backlinks]] link in my vault to [[Backlink]] so they all point at the same page", "should_trigger": False},
  {"query": "write a python function that checks whether an HTTP method is idempotent according to RFC 9110", "should_trigger": False},
  {"query": "내 Backlink 노트 frontmatter 키 순서가 알파벳 순인지 lint 돌려줘", "should_trigger": False},
  {"query": "is my Spaced Repetition page right that Ebbinghaus discovered the forgetting curve in 1885? check it against sources", "should_trigger": False}
 ]}

concept = {
 "skill_name": "concept", "fixture": "evals/fixture-vault", "baseline_skill": "principle-knowledge-notes", "wiki": "Knowledge/",
 "evals": [
  {"id": 1, "eval_name": "new-concept-work-note", "prompt": "Projects/Lumen Notes Import Plan.md 에 적어 둔 progressive summarization 말인데, 이 방법론이 정확히 어떻게 돌아가는 거야? 짧은 노트에도 쓸 만해?",
   "expected_output": "Creates Knowledge/Concepts/Progressive Summarization.md from assets/concept.md with Sources links, turns only the first mention in the work note into a wikilink, saves no Raw; reports `Wiki: created [[Progressive Summarization]]`.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Concepts/*.md", "name_regex": "(?i)^progressive summari", "state": "created"}},
   "expectations": concept_page("@page") + [first_mention("progressive summarization", "(?i)^progressive summari"), OTHER_WORK, LINT, NO_RAW, within(["Knowledge/"], ["Projects/Lumen Notes Import Plan.md"]), wiki_line("created", "Progressive Summari")]},
  {"id": 2, "eval_name": "existing-concept-update", "prompt": "Spaced repetition 이랑 Leitner system 은 어떻게 연결돼? 전에 정리해 둔 간격 반복 노트에 보태줘.",
   "expected_output": "Updates Knowledge/Concepts/Spaced Repetition.md with the Leitner connection (no duplicate page), migrated to the concept template; reports `Wiki: updated [[Spaced Repetition]]`.",
   "files": ["evals/fixture-vault"], "targets": {},
   "expectations": [
     {"text": "No duplicate Spaced Repetition page is created", "check": "count_created", "glob": "*", "name_regex": "(?i)spaced|간격", "max": 0},
     {"text": "Knowledge/Concepts/Spaced Repetition.md is updated", "check": "modified", "file": "Knowledge/Concepts/Spaced Repetition.md"},
     {"text": "Spaced Repetition keeps layer: concepts, with no status key", "check": "frontmatter", "file": "Knowledge/Concepts/Spaced Repetition.md", "equals": {"layer": "concepts"}, "absent": ["status"]},
     {"text": "Spaced Repetition body uses only assets/concept.md sections, in template order, with Key Insight, Overview, Details and Sources", "check": "headings", "file": "Knowledge/Concepts/Spaced Repetition.md", "template": "skills/concept/assets/concept.md", "required": ["## Overview", "## Details", "## Sources"], "callouts": ["> [!tip] Key Insight"]},
     refs("Knowledge/Concepts/Spaced Repetition.md", "## Sources"),
     LINT, NO_RAW, within(["Knowledge/"]), wiki_line("updated", "Spaced Repetition")]},
 ],
 "trigger_evals": [
  {"query": "I want to try the Zettelkasten method for my research notes this winter - how does it actually work and what's the core idea?", "should_trigger": True},
  {"query": "Tiago Forte 의 Progressive Summarization 이 정확히 어떤 방법인지, 짧은 노트에도 쓸 만한지 정리해줘", "should_trigger": True},
  {"query": "Explain Jobs To Be Done as a framework and capture it as a note in my wiki", "should_trigger": True},
  {"query": "first principles thinking 이 방법론으로서 어떻게 작동하는지 개념 노트로 남겨줘", "should_trigger": True},
  {"query": "what's the feynman technique and how would i use it to study linear algebra? write it up in my vault", "should_trigger": True},
  {"query": "My Spaced Repetition concept page doesn't mention the Leitner box approach - research it and update the page", "should_trigger": True},
  {"query": "OKR 프레임워크를 우리 팀에 도입하려는데 핵심 원리랑 한계가 뭔지 알려줘", "should_trigger": True},
  {"query": "can you explain the CODE method from Building a Second Brain (capture, organize, distill, express) and add a page for it", "should_trigger": True},
  {"query": "Pomodoro technique 이 왜 효과가 있다고 하는지 근거까지 포함해서 노트 만들어줘", "should_trigger": True},
  {"query": "I keep hearing about 'atomic notes' as a note-taking pattern. what's the idea, and where does it break down?", "should_trigger": True},
  {"query": "what does 'idempotent' mean? my reviewer used it about my retry endpoint", "should_trigger": False},
  {"query": "'메타인지' 라는 단어 뜻만 정확히 알려줘", "should_trigger": False},
  {"query": "Who makes Obsidian and how is the company funded? add an organization page", "should_trigger": False},
  {"query": "Readwise Reader 앱 어떤 건지 알려줘, 하이라이트 동기화도 돼?", "should_trigger": False},
  {"query": "Ingest this article I'm pasting about the Feynman technique into my vault and keep the original text: 'The Feynman Technique has four steps...'", "should_trigger": False},
  {"query": "last month i studied GTD - what did i conclude in my notes about weekly reviews?", "should_trigger": False},
  {"query": "Is my Zettelkasten page right that Luhmann published 70 books? double-check it against sources", "should_trigger": False},
  {"query": "Implement the SM-2 spaced repetition scheduler in TypeScript for my flashcard app", "should_trigger": False},
  {"query": "Projects/Thesis.md 제목 구조만 깔끔하게 정리해줘, 내용은 추가하지 말고", "should_trigger": False},
  {"query": "Make a MOC that lists all my productivity method notes", "should_trigger": False}
 ]}

JANE = "Knowledge/People/Jane Doe.md"
IMPRESSION = "I met Jane at a meetup in October. She explained the product more clearly than its own website does, and I want to follow what she ships next."
entity = {
 "skill_name": "entity", "fixture": "evals/fixture-vault", "baseline_skill": "principle-knowledge-notes", "wiki": "Knowledge/",
 "evals": [
  {"id": 1, "eval_name": "new-product-work-note", "prompt": "Projects/Lumen Notes Import Plan.md 보다가 궁금해졌는데, Readwise Reader 는 어떤 앱이야? 하이라이트를 Lumen 으로 넘길 수 있을지 알고 싶어.",
   "expected_output": "Creates Knowledge/Products/Readwise Reader.md from assets/product.md (url plain, other URLs under *_url, Lumen Notes wikilinked), turns only the first mention in the work note into a wikilink; reports `Wiki: created [[Readwise Reader]]`.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Products/*.md", "name_regex": "(?i)^readwise reader", "state": "created"}},
   "expectations": entity_page("@page", "product", ["## Origin", "## Explanation", "## References"]) + [
     {"text": "Product frontmatter carries the homepage as a plain `url`", "check": "frontmatter", "file": "@page", "contains": {"url": "^https?://\\S+$"}},
     refs("@page", "## References"),
     first_mention("Readwise Reader", "(?i)^readwise reader"), OTHER_WORK, LINT, NO_RAW,
     within(["Knowledge/"], ["Projects/Lumen Notes Import Plan.md"]), wiki_line("created", "Readwise Reader")]},
  {"id": 2, "eval_name": "person-update-impressions", "prompt": "Jane Doe 가 Northwind Labs CTO 가 됐대. Sources 에 [[2026-11-25 Northwind Labs leadership update]] 로 저장해 뒀어. 그 사람 페이지 업데이트해줘.",
   "expected_output": "Adds a dated `## Updates` line citing the Raw, moves the owner's impressions verbatim to Notes/2026-10-02 Jane Doe.md (authorship: user, related [[Jane Doe]]), links it back from the person page, sets authorship: mixed; reports `Wiki: updated [[Jane Doe]]`.",
   "files": ["evals/fixture-vault"], "targets": {"note": {"glob": "Notes/2026-10-02 Jane Doe.md", "state": "created"}},
   "expectations": [
     {"text": "A dated line under ## Updates states the CTO appointment and links [[2026-11-25 Northwind Labs leadership update]]", "check": "section_line", "file": JANE, "heading": "## Updates", "regex": r"(?i)^- \[\[2026-11-2[56]\]\] (?![^\n]*\b(?:not|never|denied|rumou?red)\b)(?=[^\n]*(?:\b(?:appoint(?:ed|ment)|promot(?:ed|ion)|named|became|becomes|took over|assumed)\b|임명|선임|취임|승진|[가이] (?:됐|되었)))(?=[^\n]*(?:\b(?:CTO|Chief Technology Officer)\b|최고기술책임자))[^\n]*\[\[(?:Sources/)?2026-11-25 Northwind Labs leadership update(?:\|[^\]]*)?\]\]"},
     {"text": "Exactly one impressions note is created, at Notes/2026-10-02 Jane Doe.md ({date_created} {Name})", "check": "count_created", "glob": "Notes/*", "name_regex": "^2026-10-02 Jane Doe\\.md$", "min": 1, "max": 1},
     {"text": "The owner's impression sentences move byte-exact from the person page body to the impressions note body", "check": "moved_verbatim", "sentences": IMPRESSION, "from": JANE, "to": "@note"},
     {"text": "The impressions note has authorship: user and related [[Jane Doe]]", "check": "frontmatter", "file": "@note", "equals": {"authorship": "user"}, "contains": {"related": "^\\[\\[Jane Doe\\]\\]$"}},
     {"text": "The person page links the impressions note in related, is authorship: mixed, keeps layer: entities and has no status", "check": "frontmatter", "file": JANE, "equals": {"authorship": "mixed", "layer": "entities"}, "contains": {"related": "^\\[\\[2026-10-02 Jane Doe\\]\\]$"}, "absent": ["status"]},
     {"text": "Person body uses only assets/person.md sections, in template order, with the TL;DR callout and Updates (no Impressions section)", "check": "headings", "file": JANE, "template": "skills/entity/assets/person.md", "required": ["## Updates"], "callouts": ["> [!abstract] TL;DR"]},
     SRC_SAME, LINT, dict(within(["Knowledge/"], ["Notes/2026-10-02 Jane Doe.md"]), text="Writes stay under Knowledge/ except the exact impressions note Notes/2026-10-02 Jane Doe.md"), wiki_line("updated", "Jane Doe")]},
 ],
 "trigger_evals": [
  {"query": "Logseq 이라는 앱 들어봤어? Lumen Notes 랑 비교하면 어떤 앱인지 궁금해", "should_trigger": True},
  {"query": "Who is Tiago Forte? I keep seeing his name everywhere - add him to my people notes", "should_trigger": True},
  {"query": "Readwise Reader is on my radar for highlight management. what is it, who makes it, and how does its sync work?", "should_trigger": True},
  {"query": "Anthropic 이라는 회사 어떤 곳인지 조직 페이지 하나 만들어줘", "should_trigger": True},
  {"query": "Jane Doe got promoted to CTO at Northwind Labs this week - update her page", "should_trigger": True},
  {"query": "The book 'How to Take Smart Notes' by Sönke Ahrens - record it in my vault, I'm starting it this week", "should_trigger": True},
  {"query": "Lex Fridman 팟캐스트 채널 페이지 만들어줘, 자주 듣거든", "should_trigger": True},
  {"query": "add the paper 'Attention Is All You Need' (Vaswani et al., 2017) to my vault as a paper note, doi 10.48550/arXiv.1706.03762", "should_trigger": True},
  {"query": "what's Playwright MCP and how does it actually drive the browser? i want to use it for a scraping side project", "should_trigger": True},
  {"query": "성수동 '대림창고' 카페 가봤는데 장소 노트 남겨줘", "should_trigger": True},
  {"query": "what's the difference between a library and a framework in software, conceptually?", "should_trigger": False},
  {"query": "Explain the idea of local-first software and its seven ideals", "should_trigger": False},
  {"query": "'RAG' 가 무슨 뜻이야? 용어 정리해줘", "should_trigger": False},
  {"query": "here's the PDF of the Attention Is All You Need paper (~/Downloads/1706.03762.pdf) - ingest it and keep the full text as a Raw", "should_trigger": False},
  {"query": "Write a Playwright test that logs into our staging site and checks the dashboard loads", "should_trigger": False},
  {"query": "what did i write last year about Notion vs Obsidian in my notes?", "should_trigger": False},
  {"query": "Is it still true that my Lumen Notes page says the app is free? check it against its sources", "should_trigger": False},
  {"query": "Fix the broken links in my People folder", "should_trigger": False},
  {"query": "Draft a short email to Jane Doe congratulating her on the CTO promotion", "should_trigger": False},
  {"query": "노트 앱 처음 쓰는 대학생한테 추천할 만한 거 3개만 골라줘, 이유랑 같이", "should_trigger": False}
 ]}

ARTICLE = """이 글 ingest 해줘. 모으는 목적: Lumen Notes 평가 프로젝트.

Lumen Notes 1.0 is out — Northwind Labs blog, 2026-11-26 (https://lumen.example.com/blog/1-0)

Today Northwind Labs ships Lumen Notes 1.0. The headline feature is block references: you can link to a single paragraph in another note, and that paragraph shows how many notes cite it. Jane Doe, now our CTO, says block references were the most requested feature of the beta. After a 30-day trial, Lumen Notes 1.0 costs $8 a month."""
SOLVED = """(Earlier in this conversation)
Me: Lumen Notes 에서 노트 이름을 바꾸면 다른 노트에 걸린 링크가 깨져. 어떻게 해?
You: Settings → Links 에서 'Update links on rename' 을 켜고, 이미 깨진 링크는 Command palette 의 'Find broken links' 로 찾은 다음 각 항목에서 'Relink' 로 새 이름에 다시 연결해 보세요.

Me (now): 해봤는데 됐어! 'Update links on rename' 켜고, 'Find broken links' 로 찾은 깨진 링크 12개를 'Relink' 로 다 고쳤어. 이름 하나 더 바꿔 봤는데 이번엔 링크가 그대로 살아 있어. 고마워."""
mode = {
 "skill_name": "secondbrain-mode", "fixture": "evals/fixture-vault", "baseline_skill": "ingest", "mode": True, "wiki": "Knowledge/",
 "evals": [
  {"id": 1, "eval_name": "unknown-word-to-term", "prompt": "What does 'idempotent' mean? Our reviewer linked https://developer.mozilla.org/en-US/docs/Glossary/Idempotent and said my retry endpoint isn't idempotent.",
   "expected_output": "Answers the question; a term subagent writes Knowledge/Terms/Idempoten*.md; the MDN link stays a [label](URL) link; last line `Wiki: created [[Idempotence]]`.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Terms/*.md", "name_regex": "(?i)^idempoten", "state": "created"}},
   "expectations": mode_common("term") + [{"text": "The Term page exists in Knowledge/Terms/", "check": "exists", "file": "@page"}, LINT, NO_RAW, within(["Knowledge/"]), wiki_line("created", "Idempoten")]},
  {"id": 2, "eval_name": "methodology-to-concept", "prompt": "I want to try the Zettelkasten method for my research notes this winter. How does it actually work, and what's the core idea behind it?",
   "expected_output": "Answers; a concept subagent writes Knowledge/Concepts/Zettelkasten*.md; last line `Wiki: created [[Zettelkasten]]`.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Concepts/*.md", "name_regex": "(?i)zettelkasten", "state": "created"}},
   "expectations": mode_common("concept") + [{"text": "The Concept page exists in Knowledge/Concepts/", "check": "exists", "file": "@page"}, LINT, NO_RAW, within(["Knowledge/"]), wiki_line("created", "Zettelkasten")]},
  {"id": 3, "eval_name": "product-to-entity", "prompt": "Logseq 라는 앱 들어봤어? Lumen Notes 랑 비교하면 어떤 앱인지 궁금해.",
   "expected_output": "Answers; an entity subagent writes Knowledge/Products/Logseq.md with [[Lumen Notes]] linked; last line `Wiki: created [[Logseq]]`.",
   "files": ["evals/fixture-vault"], "targets": {"page": {"glob": "Knowledge/Products/*.md", "name_regex": "(?i)^logseq", "state": "created"}},
   "expectations": mode_common("entity") + [{"text": "The Product page exists in Knowledge/Products/", "check": "exists", "file": "@page"}, LINT, NO_RAW, within(["Knowledge/"]), wiki_line("created", "Logseq")]},
  {"id": 4, "eval_name": "article-handover-to-ingest", "prompt": ARTICLE,
   "expected_output": "An ingest subagent saves the article as a Raw in Sources/, compiles it into the wiki and updates Tools MOC; last line `Wiki: created ..., updated ...`.",
   "files": ["evals/fixture-vault"], "targets": {},
   "expectations": mode_common("ingest") + [
     {"text": "The handed-over article is saved as a Raw in Sources/", "check": "count_created", "glob": "Sources/*.md", "min": 1},
     {"text": "The related MOC (Knowledge/Maps/Tools MOC.md) is updated with a link to a page this ingest created", "check": "links_new_page", "file": "Knowledge/Maps/Tools MOC.md"},
     {"text": "Both configured wiki records are updated (Knowledge/index.md and Knowledge/log.md)", "check": "records_updated", "files": ["Knowledge/index.md", "Knowledge/log.md"]},
     LINT, SRC_SAME, within(["Knowledge/", "Sources/", "Notes/2026-10-02 Jane Doe.md"]),
     FOOTER_ANY]},
  {"id": 5, "eval_name": "past-study-to-query", "prompt": "전에 spaced repetition 공부해서 정리해 둔 게 있었는데, 핵심이 뭐였지?",
   "expected_output": "A query subagent reads Knowledge/Concepts/Spaced Repetition.md and the answer gives its cited content; nothing written outside the wiki; a Wiki line only if a page was written.",
   "files": ["evals/fixture-vault"], "targets": {},
   "expectations": mode_common("query", writes=False) + [
     {"text": "The answer cites the existing page [[Spaced Repetition]]", "check": "answer_line", "regex": "\\[\\[Spaced Repetition"},
     {"text": "The answer gives the page's content: reviews spaced so material returns just before it would be forgotten", "check": "answer_line", "regex": "(?i)(forgotten|forget|잊(기|어버리기|히기|혀지기|어버릴)? ?(직전|전에|바로 전))"},
     NO_RAW, within(["Knowledge/"]), FOOTER_OPT]},
  {"id": 6, "eval_name": "doubt-to-verify", "prompt": "Lumen Notes 페이지에 Jane Doe 가 디자인 리드라고 돼 있던데, 그거 아직 맞아? 출처 다시 확인해 봐.",
   "expected_output": "A background verify subagent checks the claim against the Raws (the 2026-11-25 leadership update makes her CTO). The source-check request authorizes no writes, and there is no Wiki line.",
   "files": ["evals/fixture-vault"], "targets": {},
   "expectations": mode_common("verify", writes=False) + [
     {"text": "The answer concludes from the 2026-11-25 leadership update that Jane Doe is now CTO", "check": "answer_line", "regex": "(?i)(CTO|Chief Technology Officer|최고기술책임자)"},
     {"text": "The answer cites the newer source (the 2026-11-25 leadership update)", "check": "answer_line", "regex": "(?i)(2026-11-25|11-25|leadership update|리더십)"},
     {"text": "The entire vault stays byte-identical: no creates, edits or deletions", "check": "no_changes_under", "prefix": ""},
     {"text": "The report-only answer has no Wiki line", "check": "answer_no_wiki_line"}]},
  {"id": 7, "eval_name": "solved-howto-guide", "prompt": SOLVED,
   "expected_output": "The How-to solved and confirmed in the conversation becomes a Guide page (layer: guides) in Knowledge/Guides/ from the ingest guide template, with no Raw and no MOC; last line `Wiki: created [[...]]`.",
   "files": ["evals/fixture-vault"], "targets": {"guide": {"glob": "Knowledge/Guides/*.md", "name_regex": "", "state": "created"}},
   "expectations": [
     {"text": "The guide is written by ingest in a finished background subagent that opened ingest/SKILL.md and wrote it; the main thread writes nothing to the wiki", "check": "routed", "skill": "ingest", "writes": True},
     mode_common("ingest")[1],
     {"text": "A Guide page (layer: guides) is created in Knowledge/Guides/", "check": "count_created", "glob": "Knowledge/Guides/*.md", "frontmatter_equals": {"layer": "guides"}, "min": 1},
     {"text": "The Guide uses only the guide template sections, in order, with Key Insight, Overview and Details", "check": "headings", "file": "@guide", "template": "skills/ingest/templates/guide.md", "required": ["## Overview", "## Details"], "callouts": ["> [!tip] Key Insight"]},
     {"text": "The Guide's Procedure contains the confirmed steps: 'Update links on rename', 'Find broken links' and 'Relink'", "check": "section_line", "file": "@guide", "heading": "### Procedure", "patterns": [r"\bUpdate links on rename\b", r"\bFind broken links\b", r"\bRelink\b"]},
     {"text": "A chat-only Guide touches no Map (MOC)", "check": "unchanged", "files": ["Knowledge/Maps/*"]},
     NO_RAW, LINT, within(["Knowledge/"]),
     {"text": "The answer's last line is the only `Wiki:` line, names the Guide as created, and its pages are exactly the wiki pages written", "check": "footer_matches", "require": {"created": ["."]}}]},
  {"id": 8, "eval_name": "unsolved-howto-no-guide", "prompt": "Lumen Notes 에서 transclusion 한 노트를 plain text 로 export 하는 방법 알아? 'Export as Markdown' 이랑 'Flatten embeds' 둘 다 해봤는데 embed 가 그대로 남아. 아직 못 풀었어.",
   "expected_output": "No Guide page is created for the unsolved How-to; an unknown word may still go to term; Wiki line only if something was written.",
   "files": ["evals/fixture-vault"], "targets": {},
   "expectations": [
     {"text": "No Guide page (layer: guides) is created for the unsolved How-to", "check": "count_created", "glob": "*", "frontmatter_equals": {"layer": "guides"}, "max": 0},
     {"text": "Nothing is created, modified or deleted in the Guides folder", "check": "no_changes_under", "prefix": "Knowledge/Guides/"},
     mode_common("ingest")[1], NO_RAW, LINT, within(["Knowledge/"]), FOOTER_OPT]},
 ],
 "trigger_evals": [
  {"query": "/secondbrain-mode", "should_trigger": True},
  {"query": "turn on secondbrain mode for the rest of this session", "should_trigger": True},
  {"query": "secondbrain mode 켜줘. 이제부터 대화하면서 모르는 단어 나오면 위키에 써 줘", "should_trigger": True},
  {"query": "secondbrain mode off - stop writing to the wiki for now", "should_trigger": True},
  {"query": "세컨드브레인 모드 꺼줘", "should_trigger": True},
  {"query": "enable secondbrain mode, then explain what a monad is", "should_trigger": True},
  {"query": "what's a monad in functional programming?", "should_trigger": False},
  {"query": "ingest this article into my vault: 'Lumen Notes 1.0 is out...'", "should_trigger": False},
  {"query": "turn on dark mode in Obsidian and make the sidebar narrower", "should_trigger": False},
  {"query": "secondbrain-skills 플러그인 지금 버전이 몇이야?", "should_trigger": False},
  {"query": "what does my second brain say about spaced repetition?", "should_trigger": False},
  {"query": "help me design a 'second brain' system in Notion for my team's onboarding docs", "should_trigger": False},
  {"query": "lint my vault and list the broken links", "should_trigger": False},
  {"query": "Who is Tiago Forte? add him to my people notes", "should_trigger": False}
 ]}

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    if here.name != "evals":
        here = Path.cwd() / "evals"
    for spec in (term, concept, entity, mode):
        path = here / spec["skill_name"] / "evals.json"
        path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(path)
