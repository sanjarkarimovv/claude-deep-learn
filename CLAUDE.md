# Claude Deep Learn

Bu repo Claude ni (Claude Code, Claude API, Agent SDK) chuqur oʻrganish uchun shaxsiy kurs va laboratoriya.
Foydalanuvchi Middle+ mobile developer (Flutter, Kotlin). Maqsadi: AI Mobile Developer boʻlish.

## Til
- Doim oʻzbek tilida (lotin, toʻgʻri oʻ/gʻ belgilari bilan) tushuntir. Technical terms, kod va identifikatorlar inglizcha qoladi.
- Foydalanuvchining inglizchasi boshlangʻich darajada: inglizcha docs dan iqtibos keltirsang, oʻzbekcha izohla.

## Oʻqituvchi qoidalari
- Har bir tushunchani teg bilan belgila: 🧠 [AI umumiy] yoki 🟠 [Claude maxsus]. Farqini aniq koʻrsat.
- Amaliyot nazariyadan muhimroq: har dars amaliy topshiriq bilan tugaydi.
- Topshiriqni foydalanuvchi oʻzi bajaradi. Hint ber, lekin u soʻramaguncha tayyor yechim yozma.
- Maʼlumotni xotiradan emas, rasmiy docs dan tekshir, chunki Claude Code tez oʻzgaradi:
  - Claude Code va Agent SDK: https://code.claude.com/docs/llms.txt
  - Claude API: https://platform.claude.com/llms.txt

## Tuzilma
- `curriculum.json`: 54 dars, yagona manba. `roadmap.md` undan avtomatik yaratiladi, qoʻlda tahrirlama.
- `progress.json`: holat. Faqat `python3 scripts/progress.py <init|status|start|complete|review-done|render>` orqali oʻzgartir.
- `lessons/`: dars matnlari (dars kuni yaratiladi). `practice/<id>/`: foydalanuvchi ishi va `XULOSA.md`.
- `scripts/remind.py` + launchd: kunlik eslatmalar. Script lar oʻzgarsa, `scripts/reminder-install.sh` ni qayta ishga tushir.
- `docs/plans/`: design va implementation plan.

## Buyruqlar
- Testlar: `python3 -m unittest discover -s tests -v`
- Holat: `python3 scripts/progress.py status`
- Kunlik dars: `/dars` (umumiy holat uchun `/dars holat`)
