# SQuAD RAG Tutorial

Учебный RAG-проект на основе датасета **SQuAD 2.0**.

Проект показывает полный pipeline:

```text
data/raw/datasets.json
→ ingestion
→ chunking
→ TF-IDF index
→ retrieval
→ demo-answer
→ Streamlit UI
```

## Что делает проект

Пользователь задаёт вопрос на английском языке.

Система:

1. ищет релевантные фрагменты из SQuAD 2.0;
2. показывает найденные источники;
3. формирует demo-ответ;
4. отказывается отвечать, если релевантного контекста нет.

Проект реализован без внешней LLM. Ответ формируется только на основе найденных фрагментов и metadata из датасета.

## Данные

Используется **SQuAD 2.0** — датасет вопросов и ответов на основе фрагментов Wikipedia.

В проекте подготовлена выборка:

```text
data/raw/datasets.json
```

Формат одной записи:

```json
{
  "id": "squad_00000",
  "title": "Beyoncé",
  "text": "Wikipedia context...",
  "source": "SQuAD 2.0 / Wikipedia",
  "questions": [
    {
      "question": "When did Beyonce start becoming popular?",
      "answer": "in the late 1990s",
      "is_impossible": false
    }
  ]
}
```

В текущей версии проекта используется 1200 записей.

## Требования

- Python 3.10+
- uv

## Установка

```bash
uv sync
```

## Сборка индекса

```bash
uv run python scripts/build_index.py
```

После запуска создаются файлы индекса:

```text
data/index/vectorizer.pkl
data/index/matrix.npz
data/index/chunks.jsonl
```

## Запуск Streamlit UI

```bash
uv run streamlit run app/main.py
```

После запуска откройте в браузере:

```text
http://localhost:8501
```

## Demo-вопросы

В интерфейсе доступны demo-вопросы:

| Вопрос | Ожидаемый результат |
|---|---|
| When did Beyonce start becoming popular? | Ответ: in the late 1990s |
| What areas did Beyonce compete in when she was growing up? | Ответ: singing and dancing |
| In what city and state did Beyonce grow up? | Ответ по найденному контексту |
| What is the price of the newest iPhone? | Отказ без выдумок |

## Проверка retrieval

```bash
uv run python scripts/check_retrieval.py
```

Ожидаемый результат: вывод top-k фрагментов с полями:

```text
doc_id
score
title
source
text
```

## Проверка demo-answer

```bash
uv run python scripts/check_generator.py
```

Ожидаемый результат:

- релевантные вопросы дают ответ и источники;
- нерелевантный вопрос даёт отказ;
- пустой вопрос просит ввести вопрос.

## Тесты

```bash
uv run pytest tests/ -v
```

Все тесты должны завершиться успешно.

## Основные команды

```bash
uv sync
uv run python scripts/build_index.py
uv run streamlit run app/main.py
uv run pytest tests/ -v
```

## Структура проекта

```text
rag-homework/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── chunker.py
│   ├── retriever.py
│   ├── generator.py
│   ├── prompts.py
│   └── main.py
├── scripts/
│   ├── prepare_datasets.py
│   ├── ingest.py
│   ├── build_index.py
│   ├── check_retrieval.py
│   └── check_generator.py
├── data/
│   ├── raw/
│   │   └── datasets.json
│   ├── processed/
│   └── index/
├── tests/
│   ├── test_chunking.py
│   └── test_retrieval.py
├── doc/
│   ├── 00_project_idea.md
│   ├── vision.md
│   ├── conventions.md
│   ├── tasklist.md
│   └── workflow.md
├── pyproject.toml
├── uv.lock
└── README.md
```

## Ограничения MVP

- Используется TF-IDF, а не embedding-модель.
- Ответ формируется без внешней LLM.
- Система отвечает только при наличии релевантного контекста.
- Генерируемые артефакты `data/processed/` и `data/index/` не хранятся в Git.
- Поиск основан на словах и n-граммах, поэтому семантические переформулировки могут находиться хуже.

## Как воспроизвести проект с нуля

```bash
uv sync
uv run python scripts/build_index.py
uv run streamlit run app/main.py
```

Для проверки тестов:

```bash
uv run pytest tests/ -v
```