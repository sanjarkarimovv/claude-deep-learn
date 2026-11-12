# Claude Deep Learn

Claude Code va Claude API ni professional darajada oʻrganish uchun 54 darslik amaliy roadmap.
Darslarni `/dars` skill boshqaradi. Har kuni amaliy topshiriq bor, eslatmalar esa dars unutilmasligini taʼminlaydi.

**Maqsad:** AI Mobile Developer.

## Qanday ishlaydi
- `/dars`: keyingi darsni boshlaydi yoki topshiriqni tekshiradi
- `/dars holat`: progress, streak va keyingi mavzular
- [`roadmap.md`](roadmap.md): toʻliq xarita (avtomatik yangilanadi)
- Eslatmalar (macOS): `scripts/reminder-install.sh`, oʻchirish uchun `scripts/reminder-uninstall.sh`

🧠 AI umumiy · 🟠 Claude maxsus · 📱 Amaliy loyiha

## Tuzilma
| Yoʻl | Vazifasi |
|---|---|
| `curriculum.json` | 54 dars (yagona manba) |
| `progress.json` | Joriy holat (`scripts/progress.py` boshqaradi) |
| `lessons/` | Dars matnlari |
| `practice/` | Topshiriqlar va xulosalar |
| `.claude/skills/dars/` | `/dars` skill |
| `docs/plans/` | Design va implementation plan |

## Testlar
```bash
python3 -m unittest discover -s tests -v
```
