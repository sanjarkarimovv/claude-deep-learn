# 🗺️ Claude Deep Learn Roadmap

> Bu fayl avtomatik yaratiladi (`scripts/progress.py`). Qoʻlda tahrirlamang.

**Progress:** `░░░░░░░░░░░░░░░░░░░░` 0/54

🧠 AI umumiy · 🟠 Claude maxsus · 📱 Amaliy loyiha · ✅ bajarildi · 👉 joriy · ⬜ navbatda

## 00. AI asoslari

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| 👉 | 00-01 | 🧠 | LLM qanday ishlaydi | Next-token prediction, transformer va training bosqichlarini tushunish |
| ⬜ | 00-02 | 🧠 | Tokens va context window | Token nima, context window chegarasi va narx qanday hisoblanishini bilish |
| ⬜ | 00-03 | 🧠 | Sampling, hallucination va cheklovlar | Temperature, knowledge cutoff va hallucination sabablarini tushunish |
| ⬜ | 00-04 | 🧠 | Prompt engineering asoslari | Aniq koʻrsatma, misollar (few-shot), rol va bosqichma-bosqich fikrlash texnikalari |
| ⬜ | 00-05 | 🧠 | Agents va tool use konsepsiyasi | Agentic loop (think → act → observe) va tool calling qanday ishlashini tushunish |
| ⬜ | 00-06 | 🧠 | Embeddings, RAG va evals | Vector search, retrieval va AI sifatini oʻlchash (evals) asoslarini bilish |

## 01. Claude ekotizimi

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 01-01 | 🟠 | Claude model family va model tanlash | Opus, Sonnet, Haiku va Fable farqlari, narxlari va qaysi vazifaga qaysi model |
| ⬜ | 01-02 | 🟠 | Thinking va effort | Thinking va effort darajalari sifat, tezlik va narxga qanday taʼsir qilishini bilish |
| ⬜ | 01-03 | 🟠 | Claude surfaces va Claude uchun prompting | claude.ai, Claude Code, Desktop, Web, mobile va API qachon kerakligi; XML tags bilan prompting |

## 02. Claude Code asoslari

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 02-01 | 🟠 | Claude Code qanday ishlaydi | Agentic loop, built-in tools va Claude Code arxitekturasini tushunish |
| ⬜ | 02-02 | 🟠 | Interactive mode va buyruqlar | Slash commands, @ mentions, ! bash mode va shortcut larni erkin ishlatish |
| ⬜ | 02-03 | 🟠 | .claude papka va CLAUDE.md | Memory ierarxiyasi (user, project, local), /init va CLAUDE.md best practices |
| ⬜ | 02-04 | 🟠 | Context window boshqaruvi | /context, /compact, /clear va prompt caching bilan context ni samarali boshqarish |
| ⬜ | 02-05 | 🟠 | Sessions | Session larni resume, continue, fork qilish va nomlash |
| ⬜ | 02-06 | 🟠 | Permission modes va permissions | default, acceptEdits, plan va auto rejimlari hamda allow/deny qoidalarini tushunish |
| ⬜ | 02-07 | 🟠 | Checkpointing va model sozlamalari | /rewind bilan oʻzgarishlarni qaytarish, /model, fast mode va advisor ni ishlatish |

## 03. Professional workflow

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 03-01 | 🟠 | Claude Code best practices | Explore → plan → code → commit oqimi va aniq prompt yozish qoidalari |
| ⬜ | 03-02 | 🟠 | Plan mode chuqur | Plan mode qachon kerakligini bilish, plan ni tahrirlash va tasdiqlash |
| ⬜ | 03-03 | 🟠 | Git workflow va worktrees | Claude bilan commit, branch, PR va parallel worktree session lar |
| ⬜ | 03-04 | 🟠 | Claude bilan debugging | Xatoni reproduce qilish, log tahlili va root cause ni topish metodikasi |
| ⬜ | 03-05 | 🟠 | Claude bilan TDD | Test-first prompting va verification loop orqali ishonchli kod yozish |
| ⬜ | 03-06 | 🟠 | Code review va xavfsizlik | /code-review, security guidance va ultrareview imkoniyatlarini ishlatish |

## 04. Customization

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 04-01 | 🟠 | Settings va precedence | User, project, local va managed settings qatlamlari qanday ishlashini tushunish |
| ⬜ | 04-02 | 🟠 | Chuqur permissions va sandboxing | Murakkab permission qoidalari va sandboxed Bash bilan xavfsiz ishlash |
| ⬜ | 04-03 | 🟠 | Skills I: skill anatomiyasi | SKILL.md tuzilishi, frontmatter, arguments va dynamic context injection |
| ⬜ | 04-04 | 🟠 | Skills II: oʻz skill ingizni yaratish | Real ish uchun qayta ishlatiladigan skill yozish va sinash |
| ⬜ | 04-05 | 🟠 | Subagents | Built-in va custom subagent lar, ularning context va tool cheklovlari |
| ⬜ | 04-06 | 🟠 | Hooks | Lifecycle event lar (PreToolUse, PostToolUse, Stop) bilan automation qurish |
| ⬜ | 04-07 | 🟠 | MCP | MCP protokoli, server ulash, scope lar va xavfsizlik |
| ⬜ | 04-08 | 🟠 | Output styles, statusline va keybindings | Claude Code interfeysi va javob uslubini oʻzingizga moslash |
| ⬜ | 04-09 | 🟠 | Plugins | Plugin larni oʻrnatish, marketplace lar va oʻz plugin ingizni yaratish |

## 05. Automation va multi-agent

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 05-01 | 🟠 | Headless mode | claude -p, output formatlari va Claude ni script lardan ishlatish |
| ⬜ | 05-02 | 🟠 | GitHub Actions va CI | Claude Code ni CI/CD pipeline ga ulash |
| ⬜ | 05-03 | 🟠 | Scheduled tasks va routines | /loop, cron, cloud routines va desktop scheduled tasks farqini bilish |
| ⬜ | 05-04 | 🟠 | /goal va uzoq ishlaydigan vazifalar | Claude ni aniq yakunlash sharti bilan mustaqil ishlatish |
| ⬜ | 05-05 | 🟠 | Multi-agent: parallel agents, teams va workflows | Parallel agent lar, agent teams va dynamic workflows qachon kerakligini bilish |
| ⬜ | 05-06 | 🟠 | Channels, artifacts va remote ishlash | Channels, artifacts, Remote Control, web va mobile dan Claude Code bilan ishlash |

## 06. Claude API

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 06-01 | 🟠🧠 | Messages API asoslari | API key, birinchi request, message threads va stop reasons |
| ⬜ | 06-02 | 🟠🧠 | Streaming | SSE event lari va real-time javobni qayta ishlash |
| ⬜ | 06-03 | 🟠🧠 | Tool use I: tool lar va agent loop | Tool larni aniqlash, tool call larni qayta ishlash va agent loop yozish |
| ⬜ | 06-04 | 🟠🧠 | Tool use II: server tools va tool runner | Web search, code execution, tool runner, parallel va strict tool use |
| ⬜ | 06-05 | 🟠🧠 | Structured outputs, vision va PDF | JSON schema bilan ishonchli output, rasm va PDF tahlili |
| ⬜ | 06-06 | 🟠🧠 | Prompt caching, token counting va narx | Caching bilan narx va latency ni kamaytirish, xarajatni hisoblash |
| ⬜ | 06-07 | 🟠🧠 | Context management: compaction va memory | Context editing, compaction va memory tool bilan uzun suhbatlarni boshqarish |
| ⬜ | 06-08 | 🟠🧠 | Batch, Files API, evals va guardrails | Ommaviy ishlov, fayllar, sifatni oʻlchash va prompt injection dan himoya |

## 07. Agent SDK

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 07-01 | 🟠 | Agent SDK va agent loop | Agent SDK nima, Claude Code bilan aloqasi va agent loop qanday ishlaydi |
| ⬜ | 07-02 | 🟠 | Custom tools va MCP | SDK da oʻz tool laringiz va MCP server larni ulash |
| ⬜ | 07-03 | 🟠 | Permissions, hooks va sessions | Agent xatti-harakatini nazorat qilish va session larni boshqarish |
| ⬜ | 07-04 | 🟠 | Hosting va xavfsiz deploy | Agent ni production ga xavfsiz chiqarish va xarajatni kuzatish |

## 08. Capstone: AI mobile ilova

| | ID | Teg | Mavzu | Maqsad |
|---|---|---|---|---|
| ⬜ | 08-01 | 📱 | Arxitektura va backend proxy | Flutter ilova ↔ proxy ↔ Claude API arxitekturasi va API key xavfsizligi |
| ⬜ | 08-02 | 📱 | Streaming chat UI | SSE stream ni Flutter UI ga (BLoC) ulash |
| ⬜ | 08-03 | 📱 | Mobile da tool use | Ilova funksiyalarini Claude ga tool sifatida berish |
| ⬜ | 08-04 | 📱 | Narx, xatolar va production | Prompt caching, rate limits, error handling va foydalanuvchi limitlari |
| ⬜ | 08-05 | 📱 | CI, review va yakuniy retrospektiva | Claude GitHub Actions bilan CI va butun kurs boʻyicha xulosa |
