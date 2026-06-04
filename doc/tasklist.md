# Tasklist — итерационный план разработки

Опирается на: [00_project_idea.md](00_project_idea.md) · [vision.md](vision.md) · [conventions.md](conventions.md) · [workflow.md](workflow.md)

**Правило:** одна итерация = один проверяемый результат. Не переходить дальше, пока текущий шаг не выполнен и не проверен.

---

## Отчёт по прогрессу

| Итерация | Название | Статус | Проверка |
|:--------:|----------|:------:|----------|
| 0 | Каркас проекта | ⬜ | `uv sync` без ошибок |
| 1 | Данные SQuAD 2.0 | ⬜ | `datasets.json` читается, 1000+ записей или 1000+ чанков после нарезки |
| 2 | Ingestion | ⬜ | `documents.jsonl` создан |
| 3 | Chunking | ⬜ | `chunks.jsonl` создан, тесты chunking проходят |
| 4 | Индекс TF-IDF | ⬜ | файлы индекса созданы в `data/index/` |
| 5 | Retrieval | ⬜ | поиск возвращает top-k чанков со score |
| 6 | Demo-answer | ⬜ | ответ формируется с источниками без UI |
| 7 | Streamlit UI | ⬜ | приложение запускается и показывает ответ с источниками |
| 8 | Тесты и README | ⬜ | `pytest` green, README воспроизводим |
| 9 | Документ о данных | ⬜ | `doc/DATA.md` описывает источник, масштаб и индексируемые поля |
| 10 | Сдача домашнего задания | ⬜ | `homework/SUBMISSION.md` содержит ссылку на репозиторий |

**Легенда:** ⬜ не начато · 🔄 в работе · ✅ готово · ❌ блокер

**Текущая итерация:** 0  
**Готовность MVP:** 0 / 11

---

## Итерация 0 — Каркас проекта

### Задачи

- [x] Создать `pyproject.toml`.
- [x] Добавить зависимости: `streamlit`, `scikit-learn`, `pytest`.
- [x] Создать `.gitignore`.
- [x] Добавить в `.gitignore`: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.DS_Store`, `data/index/`.
- [x] Создать папки проекта:

```text
app/
scripts/
data/raw/
data/processed/
data/index/
tests/
```

- [x] Создать `app/config.py`.
- [x] В `app/config.py` вынести пути, `top_k`, размер чанка и имена файлов индекса.

### Проверка

```bash
uv sync
uv run python -c "import app.config; print('OK')"
```

### Ожидаемый результат

Проект имеет базовую структуру, зависимости устанавливаются, конфиг импортируется без ошибок.

---

## Итерация 1 — Данные SQuAD 2.0

### Задачи

- [x] Подготовить `data/raw/datasets.json`.
- [x] Загрузить или сформировать выборку из SQuAD 2.0.
- [x] Привести записи к единому формату:

```json
{
  "id": "squad_000001",
  "title": "Article title",
  "text": "Wikipedia context text...",
  "source": "SQuAD 2.0 / Wikipedia",
  "questions": [
    {
      "question": "Question text?",
      "answer": "Answer text"
    }
  ]
}
```

- [x] Обеспечить масштаб: 1000+ текстовых записей в `datasets.json` или 1000+ чанков после нарезки.
- [x] Проверить, что у каждой записи есть `id`, `title`, `text`, `source`.

### Проверка

```bash
uv run python -c "
import json
from pathlib import Path

p = Path('data/raw/datasets.json')
data = json.loads(p.read_text(encoding='utf-8'))
items = data['datasets'] if isinstance(data, dict) and 'datasets' in data else data

assert len(items) >= 1000, f'мало записей: {len(items)}'
for item in items[:10]:
    for key in ['id', 'title', 'text', 'source']:
        assert key in item, f'нет поля {key}'
print('OK:', len(items), 'records')
"
```

### Ожидаемый результат

Исходный файл данных создан, читается Python-скриптом и содержит достаточно текстовых записей для проекта.

---

## Итерация 2 — Ingestion

### Задачи

- [x] Создать `scripts/ingest.py`.
- [x] Реализовать чтение `data/raw/datasets.json`.
- [x] Очистить текстовые поля от лишних пробелов и пустых строк.
- [x] Преобразовать записи в `data/processed/documents.jsonl`.
- [x] Сохранить metadata: `doc_id`, `title`, `source`, `questions`.

### Проверка

```bash
uv run python scripts/ingest.py
uv run python -c "
from pathlib import Path
p = Path('data/processed/documents.jsonl')
assert p.exists(), 'documents.jsonl не создан'
lines = p.read_text(encoding='utf-8').strip().splitlines()
assert len(lines) > 0, 'documents.jsonl пустой'
print('OK:', len(lines), 'documents')
"
```

### Ожидаемый результат

Создан файл `data/processed/documents.jsonl`, где каждая строка — отдельный документ с текстом и метаданными.

---

## Итерация 3 — Chunking

### Задачи

- [x] Создать `app/chunker.py`.
- [x] Реализовать нарезку документов на чанки.
- [x] Настроить максимальный размер чанка и overlap через `app/config.py`.
- [x] Сохранять для каждого чанка: `chunk_id`, `doc_id`, `title`, `source`, `text`.
- [x] Создать или обновить логику сохранения `data/processed/chunks.jsonl`.
- [x] Добавить тесты chunking.

### Проверка

```bash
uv run python scripts/build_index.py
uv run pytest tests/test_chunking.py -v
```

Дополнительная проверка файла:

```bash
uv run python -c "
from pathlib import Path
p = Path('data/processed/chunks.jsonl')
assert p.exists(), 'chunks.jsonl не создан'
lines = p.read_text(encoding='utf-8').strip().splitlines()
assert len(lines) > 0, 'chunks.jsonl пустой'
print('OK:', len(lines), 'chunks')
"
```

### Ожидаемый результат

Документы корректно нарезаются на чанки, а metadata сохраняется для дальнейшего отображения источников.

---

## Итерация 4 — Индекс TF-IDF

### Задачи

- [x] Создать `scripts/build_index.py`.
- [x] Собрать pipeline: ingestion → chunking → TF-IDF index.
- [x] Обучить `TfidfVectorizer` на текстах чанков.
- [x] Сохранить vectorizer в `data/index/vectorizer.pkl`.
- [x] Сохранить матрицу в `data/index/matrix.npz`.
- [x] Сохранить копию чанков в `data/index/chunks.jsonl`.

### Проверка

```bash
uv run python scripts/build_index.py
uv run python -c "
from pathlib import Path
required = [
    'data/index/vectorizer.pkl',
    'data/index/matrix.npz',
    'data/index/chunks.jsonl',
]
for f in required:
    assert Path(f).exists(), f'нет файла: {f}'
print('OK:', len(required), 'index files')
"
```

### Ожидаемый результат

Индекс строится одной командой, а в `data/index/` появляются все необходимые артефакты.

---

## Итерация 5 — Retrieval

### Задачи

- [x] Создать `app/retriever.py`.
- [x] Реализовать загрузку `vectorizer.pkl`, `matrix.npz`, `chunks.jsonl`.
- [x] Реализовать метод поиска по вопросу пользователя.
- [x] Использовать cosine similarity.
- [x] Возвращать top-k результатов.
- [x] Для каждого результата возвращать `text`, `doc_id`, `title`, `source`, `score`.

### Проверка

```bash
uv run python -c "
from app.retriever import Retriever

r = Retriever()
results = r.search('What is the capital of France?', k=3)

assert isinstance(results, list)
assert len(results) <= 3
if results:
    for item in results:
        assert 'doc_id' in item
        assert 'text' in item
        assert 'score' in item
print('OK:', results[:1])
"
```

### Ожидаемый результат

Retrieval работает из консоли и возвращает релевантные чанки с оценкой похожести.

---

## Итерация 6 — Demo-answer

### Задачи

- [x] Создать `app/prompts.py`.
- [x] Описать правила demo-answer: отвечать только по найденному контексту.
- [x] Создать `app/generator.py`.
- [x] Реализовать функцию `ask()` или аналогичную функцию для получения ответа.
- [x] Добавить отказ, если контекста нет или score слишком низкий.
- [x] Возвращать ответ и список источников.

### Проверка

```bash
uv run python -c "
from app.generator import ask

result = ask('What is the capital of France?')
assert 'answer' in result
assert 'sources' in result
print(result)
"
```

Negative-проверка:

```bash
uv run python -c "
from app.generator import ask

result = ask('What is the price of the newest iPhone?')
assert 'answer' in result
print(result['answer'])
"
```

### Ожидаемый результат

Система формирует demo-ответ по найденным чанкам и корректно отказывается отвечать при недостатке данных.

---

## Итерация 7 — Streamlit UI

### Задачи

- [x] Создать `app/main.py`.
- [x] Добавить поле ввода вопроса.
- [x] Добавить настройку `top_k`.
- [x] Показывать найденные фрагменты, score и источники.
- [x] Показывать итоговый demo-ответ.
- [x] Добавить сообщение, если индекс не собран.
- [x] Проверить 3 demo-вопроса и 1 negative-вопрос.

### Проверка

```bash
uv run streamlit run app/main.py
```

Demo-вопросы:

1. `When did Beyonce start becoming popular?`
2. `What areas did Beyonce compete in when she was growing up?`
3. `What is the role of Wikipedia contexts in SQuAD?`
4. Negative: `What is the price of the newest iPhone?`

### Ожидаемый результат

В браузере открывается Streamlit-приложение, которое показывает вопрос, найденные источники и demo-ответ.

---

## Итерация 8 — Тесты и README

### Задачи

- [x] Добавить `tests/test_chunking.py`.
- [x] Добавить `tests/test_retrieval.py`.
- [x] Добавить при необходимости `tests/test_generator.py`.
- [x] Обеспечить минимум 5 тестов.
- [x] Обновить корневой `README.md`.
- [x] В README указать команды запуска:

```bash
uv sync
uv run python scripts/build_index.py
uv run streamlit run app/main.py
```

- [x] Добавить в README описание проекта, данных, pipeline, demo-вопросы и negative-вопрос.

### Проверка

```bash
uv run pytest tests/ -v
```

Проверка README:

```bash
uv run python -c "
from pathlib import Path
t = Path('README.md').read_text(encoding='utf-8')
for s in ['uv sync', 'scripts/build_index.py', 'streamlit run app/main.py']:
    assert s in t, f'нет команды: {s}'
print('OK: README commands found')
"
```

### Ожидаемый результат

Тесты проходят, README позволяет запустить проект на чистой машине.

---

## Итерация 9 — Документ о данных

### Задачи

- [ ] Создать `doc/DATA.md`.
- [ ] Описать источник данных: SQuAD 2.0.
- [ ] Описать масштаб выборки.
- [ ] Описать, какие поля индексируются.
- [ ] Описать, какие поля используются как metadata.
- [ ] Указать ограничения данных.
- [ ] Добавить ссылку на `doc/DATA.md` из README.

### Проверка

```bash
uv run python -c "
from pathlib import Path

p = Path('doc/DATA.md')
assert p.exists(), 'doc/DATA.md не создан'
t = p.read_text(encoding='utf-8')
required = [
    '## Источник данных',
    '## Масштаб',
    '## Что индексируем',
    '## Metadata',
]
for s in required:
    assert s in t, f'нет раздела: {s}'
print('OK: DATA.md')
"
```

### Ожидаемый результат

Данные проекта описаны отдельно и понятно для проверяющего.

---

## Итерация 10 — Сдача домашнего задания

### Задачи

- [ ] Создать папку `homework/`, если её нет.
- [ ] Создать `homework/SUBMISSION.md`.
- [ ] Указать в `SUBMISSION.md` ссылку на репозиторий с выполненным заданием.
- [ ] Проверить, что репозиторий публичный.
- [ ] Проверить, что README содержит инструкцию запуска.
- [ ] Проверить, что Streamlit показывает источники.
- [ ] Подготовить Pull Request в исходный репозиторий задания.
- [ ] Добавить в PR файл `homework/SUBMISSION.md`.

### Проверка

```bash
uv run python -c "
from pathlib import Path
p = Path('homework/SUBMISSION.md')
assert p.exists(), 'homework/SUBMISSION.md не создан'
t = p.read_text(encoding='utf-8')
assert 'https://github.com/korn1loves/rag-homework' in t
print('OK: SUBMISSION.md')
"
```

### Ожидаемый результат

Домашнее задание готово к сдаче через Pull Request.

---

## Критерий «MVP готов»

MVP считается готовым, если выполнены все условия:

- [ ] Все итерации 0–10 отмечены как ✅ в таблице прогресса.
- [ ] Репозиторий содержит рабочий RAG-pipeline.
- [ ] `uv sync` выполняется без ошибок.
- [ ] `uv run python scripts/build_index.py` строит индекс.
- [ ] `uv run streamlit run app/main.py` запускает UI.
- [ ] Streamlit показывает найденные источники: `doc_id`, score и текст чанка.
- [ ] Есть 3 demo-вопроса с ответами.
- [ ] Есть 1 negative-вопрос с отказом.
- [ ] Есть минимум 5 тестов, и они проходят.
- [ ] README содержит инструкцию запуска.
- [ ] `doc/DATA.md` описывает источник и структуру данных.
- [ ] `homework/SUBMISSION.md` содержит ссылку на репозиторий.
