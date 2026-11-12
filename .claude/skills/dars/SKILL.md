---
name: dars
description: Claude Deep Learn kursining kunlik darsi. Keyingi darsni boshlaydi, topshiriqni tekshiradi va progress ni yangilaydi.
argument-hint: "[holat]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py *) Read Write Edit Glob Grep WebFetch
---

# /dars: kunlik oʻqituvchi

## Joriy holat (avtomatik)

!`python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py status`

Argument: `$ARGUMENTS`

## Rejimni tanlash

Yuqoridagi JSON va argument boʻyicha **faqat bitta** rejimni tanla, tartib bilan:

1. Argument `holat` boʻlsa → **Holat**
2. `current` null boʻlsa → **Kurs tugadi**
3. `mode` = `rest` boʻlsa → bugun dam olish kuni ekanini ayt. Foydalanuvchi baribir xohlasa, 5–6-qoidalar boʻyicha davom et
4. `mode` = `review`, `doneToday` = false boʻlsa → **Review**
5. `current.status` = `idle` boʻlsa → **Yangi dars**
6. `current.status` = `task_given` boʻlsa → **Tekshiruv**

## Yangi dars

1. `current.lessonFile` mavjud boʻlsa, uni oʻqi. Mavjud boʻlmasa:
   - `current.docs` dagi sahifalarni WebFetch bilan oʻqi (eng yangi maʼlumot shu yerda).
   - `${CLAUDE_SKILL_DIR}/lesson-template.md` shabloni boʻyicha dars faylini yoz. Hajmi ~10 daqiqalik oʻqish boʻlsin.
2. `current.practiceDir` ichida `TOPSHIRIQ.md` yarat: vazifa (`current.practice` asosida, ~30 daqiqa) va 3–5 ta aniq tekshiruv mezoni.
3. Run: `python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py start`
4. Foydalanuvchiga quyidagilarni koʻrsat:
   - sarlavha (`id`, `tag`, `title`);
   - nazariyaning qisqa mazmuni va dars fayliga link;
   - topshiriq va mezonlar.
   Oxirida yoz: "Bajarib boʻlgach, yana `/dars` deb yozing."

## Tekshiruv

1. `TOPSHIRIQ.md` mezonlarini oʻqi va `current.practiceDir` dagi ishni tekshir. Ish boshqa joyda boʻlsa, foydalanuvchidan soʻra.
2. Har bir mezon uchun ✅ yoki ❌ belgisi va qisqa feedback ber. ❌ boʻlsa, nimani tuzatish kerakligini ayt va **toʻxta**: progress oʻzgarmaydi.
3. 3 ta active recall savol ber, **bittadan**, har birida javobni kut. Javobni baholab, toʻgʻri javobni qisqa tushuntir.
4. `XULOSA.md` ni tekshir. Fayl yoʻq boʻlsa, foydalanuvchidan oʻz soʻzlari bilan 3–5 qator yozishni soʻra. Uni sen yozib berma.
5. Hammasi tayyor boʻlsa:
   - Run: `python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py complete --score "<toʻgʻri javoblar>/3"`
   - Natijani streak bilan nishonla va keyingi dars nomini ayt.

## Review (Shanba)

1. `practice/review-<today>/TOPSHIRIQ.md` mavjud boʻlsa, mini-loyihani tekshir (Tekshiruv dagi 1–2-qadamlar), keyin 3-qadamga oʻt.
   Mavjud boʻlmasa:
   - `thisWeek` dagi darslarning fayllarini oʻqi. Roʻyxat boʻsh boʻlsa, barcha oʻtilgan darslarni ol.
   - 5 ta quiz savoli ber (🧠 va 🟠 aralash), bittadan.
   - Hafta mavzularini birlashtiradigan 20–30 daqiqalik mini-loyihani `practice/review-<today>/TOPSHIRIQ.md` ga yoz.
2. Foydalanuvchi mini-loyihani bajargach, uni tekshir.
3. Run: `python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py review-done --score "<toʻgʻri>/5"`

## Holat

Progress bar, streak, joriy dars va `upcoming` roʻyxatini chiroyli koʻrsat, `roadmap.md` ga havola ber. Holatni oʻzgartirma.

## Kurs tugadi

Foydalanuvchini tabrikla, 54 darsning qisqa xulosasini va keyingi oʻsish yoʻnalishlarini taklif qil.

## Qoidalar

- Oʻzbek tilida yoz, technical terms inglizcha qoladi. Har bir tushunchani 🧠 yoki 🟠 bilan belgila.
- Bir dars 30–60 daqiqaga sigʻsin.
- Topshiriqni foydalanuvchi oʻzi bajaradi. Sen hint berasan, foydalanuvchi soʻrasa hint darajasini oshirasan.
- `progress.json` va `roadmap.md` ni qoʻlda tahrirlama, faqat `progress.py` orqali oʻzgartir.
