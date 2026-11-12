# Claude Deep Learn: Roadmap Design

**Sana:** 2026-11-12
**Status:** Tasdiqlangan (brainstorming yakunlandi)

## 1. Maqsad

Claude ni (birinchi navbatda Claude Code ni) professional, chuqur, "core" darajada oʻrganish. Yakuniy maqsad: **AI Mobile Developer** boʻlish.

- Bu papka darslik va laboratoriya vazifasini bajaradi. Oʻrganilgan har bir feature shu papkaning oʻziga qoʻllanadi.
- Har bir dars teg bilan ajratiladi:
  - 🧠 **[AI umumiy]**: har qanday LLM ga tegishli tushunchalar.
  - 🟠 **[Claude maxsus]**: faqat Claude ga oid bilimlar.
  - 📱 **[Amaliy]**: capstone loyiha.

## 2. Cheklovlar

| Parametr | Qiymat |
|---|---|
| Daraja | Middle+ mobile developer (Flutter, Kotlin, Clean Architecture) |
| Vaqt | Kuniga 30–60 daqiqa |
| Obuna | Claude Max |
| Til | Oʻzbekcha tushuntirish, technical terms inglizcha |
| Mobile | Oʻrgatilmaydi (user oʻzi biladi), faqat amaliyot konteksti sifatida |

## 3. Curriculum (9 modul, ~54 dars)

| # | Modul | Teg | Darslar | Asosiy mavzular |
|---|---|---|---|---|
| 0 | AI asoslari | 🧠 | 6 | LLM qanday ishlaydi, tokens, context window, sampling, hallucination, prompting, agents, RAG, embeddings, evals |
| 1 | Claude ekotizimi | 🟠 | 3 | Model family (Opus/Sonnet/Haiku/Fable), model tanlash, thinking va effort, Claude prompting best practices |
| 2 | Claude Code asoslari | 🟠 | 7 | Agentic loop, tools, `.claude/` papka, `CLAUDE.md`, memory, context boshqaruvi, sessions, permission modes, checkpointing |
| 3 | Professional workflow | 🟠 | 6 | Best practices, plan mode, git va worktrees, debugging, TDD, `/code-review` |
| 4 | Customization | 🟠 | 9 | Settings, permissions, sandboxing, skills, subagents, hooks, MCP, output styles, statusline, plugins (+ vizual HTML roadmap amaliy topshiriq) |
| 5 | Automation va multi-agent | 🟠 | 6 | Headless mode, GitHub Actions, scheduled tasks, `/loop`, `/goal`, agent teams, channels, artifacts (+ Telegram eslatma bot amaliy topshiriq) |
| 6 | Claude API | 🟠🧠 | 8 | Messages API, streaming, tool use, structured outputs, prompt caching, vision va PDF, compaction, cost |
| 7 | Agent SDK | 🟠 | 4 | Agent loop, custom tools, hooks, xavfsiz deploy |
| 8 | Capstone: AI mobile ilova | 📱 | 5 | Flutter, backend proxy (API key ilovada saqlanmaydi), Claude API streaming, tool use, CI |

**Tartib sababi:**
- 🧠 asoslar birinchi keladi: tokens va context ni bilmasdan Claude Code dagi context boshqaruvi va caching tushunarsiz qoladi.
- Claude Code API dan oldin keladi: agent loop ni amalda koʻrgandan keyin API dagi tool use oson tushuniladi.

**Haftalik ritm:**
- Dushanba–Juma: har kuni 1 ta dars.
- Shanba: review (mini-quiz va kichik loyiha).
- Yakshanba: dam olish.
- Taxminiy muddat: ~11–12 hafta.

**Manbalar:**
- Claude Code va Agent SDK: `https://code.claude.com/docs/llms.txt`
- Claude API: `https://platform.claude.com/llms.txt`

## 4. Fayl tuzilmasi

```
claude-deep-learn/
├── CLAUDE.md                  # o'qituvchi qoidalari: til, teglar, dars formati
├── .claude/skills/dars/       # /dars skill
│   ├── SKILL.md
│   └── lesson-template.md
├── curriculum.json            # 54 dars: yagona manba (id, teg, nom, maqsad, amaliyot, docs)
├── roadmap.md                 # curriculum + progress dan avtomatik yaratiladi
├── progress.json              # holat (schema pastda)
├── lessons/<NN-modul>/<id>.md # dars kuni yaratiladi
├── practice/<id>/             # user ishi + TOPSHIRIQ.md + XULOSA.md
├── scripts/
│   ├── progress.py            # holatni oʻzgartiradigan yagona CLI (testlangan)
│   ├── remind.py              # eslatma matni + osascript notification
│   ├── reminder-install.sh
│   └── reminder-uninstall.sh
├── tests/                     # unittest (32 test)
└── docs/plans/                # design va plan hujjatlari
```

## 5. `/dars` oqimi

**State machine** (`progress.json` → `current.status`):

| Holat | `/dars` nima qiladi |
|---|---|
| `idle` (yoki fayl yoʻq) | Keyingi darsni `roadmap.md` dan oladi. Rasmiy docs ni yangidan tekshiradi. `lessons/` ga dars matnini yozadi. Nazariyani (~10 daq) va topshiriqni (~30 daq, aniq mezonlar bilan) beradi. Holat `task_given` ga oʻtadi |
| `task_given` | `practice/<id>/` ni mezonlar boʻyicha tekshiradi. 2–3 ta active recall savol beradi. `XULOSA.md` ni soʻraydi. Hammasi tayyor boʻlsa, darsni ✅ qiladi, `lastCompletedDate` ni bugungi sanaga oʻrnatadi va holat yana `idle` boʻladi |

**Qoʻshimcha rejimlar:**
- **Shanba:** review rejimi. Hafta mavzulari boʻyicha quiz va mini-loyiha beriladi. Bajarilsa, `lastCompletedDate` yangilanadi.
- **`/dars holat`:** progress, streak va keyingi 5 ta mavzu.

**Qoidalar:**
- Kun oʻtkazib yuborilsa, jadval surilmaydi: qolgan joydan davom etiladi.
- Dars matni bir marta yaratiladi va `lessons/` da saqlanib qoladi.

**`progress.json` schema:**
```json
{
  "startDate": "2026-11-13",
  "lastCompletedDate": null,
  "streak": 0,
  "current": { "id": "00-01", "title": "LLM qanday ishlaydi", "status": "idle", "startedAt": null },
  "completed": [
    { "id": "00-01", "date": "2026-11-13", "quizScore": "3/3" }
  ],
  "reviews": [
    { "date": "2026-11-14", "quizScore": "4/5" }
  ]
}
```

## 6. Eslatmalar tizimi

- **Mexanizm:** macOS `launchd` LaunchAgent. Claude Code dagi `CronCreate` yoki `/loop` faqat session ochiq turganda ishlaydi, shuning uchun bu yerga mos emas.
- **Jadval:** har kuni 09:00, 10:00, …, 23:00 va 23:59 da `remind.py` ishga tushadi.
- **TCC muammosi va yechimi:** macOS `~/Desktop` ni himoyalaydi, shuning uchun `launchd` dan ishga tushgan python3 uni oʻqiy olmasligi mumkin. Yechim:
  - `progress.py` har saqlashda holat nusxasini `~/.claude-deep-learn/state.json` ga yozadi;
  - `reminder-install.sh` script larni `~/.claude-deep-learn/` ga nusxalaydi;
  - `launchd` faqat shu papka bilan ishlaydi.
- **Mantiq:** yakshanba boʻlsa yoki `lastCompletedDate == bugun` boʻlsa, script jim chiqadi. Aks holda `osascript` orqali notification koʻrsatadi.
- **Kuchayib boruvchi matn:**

| Vaqt | Ohang |
|---|---|
| 09–12 | Yumshoq: bugungi mavzu va taxminiy vaqt |
| 13–20 | Qatʼiyroq: dars hali qilinmagani haqida |
| 21–23:59 | Streak xavf ostida, kun tugashiga qolgan vaqt |

- **Uyqu rejimi:** Mac uxlagan paytda oʻtkazib yuborilgan eslatma uygʻongach bir marta koʻrsatiladi (`launchd` xatti-harakati).
- **Bir martalik sozlash:** System Settings → Notifications → "Script Editor" ga ruxsat berish.

## 7. Scope dan tashqari (YAGNI)

- **Vizual HTML roadmap:** 4-modulda amaliy topshiriq boʻladi.
- **Telefon (Telegram) eslatmalari:** 5-modulda amaliy topshiriq boʻladi.
- **54 ta dars matnini oldindan yozish:** qilinmaydi, chunki docs tez oʻzgaradi.

## 8. Muvaffaqiyat mezonlari

- `/dars` bir buyruq bilan har kungi darsni boshlaydi va yakunlaydi. "Bugun nima qilaman?" degan savol qolmaydi.
- Dars bajarilmagan kuni 09:00 dan eslatmalar keladi. Dars bajarilgandan keyin ular toʻxtaydi.
- Har bir dars 🧠 yoki 🟠 deb aniq belgilangan va amaliy topshiriqqa ega.
- Kurs oxirida tayyor natijalar boʻladi:
  - toʻliq sozlangan Claude Code muhiti (skills, hooks, MCP, plugins);
  - portfolio uchun AI mobile ilova.
