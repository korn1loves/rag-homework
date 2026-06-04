# SUBMISSION — сдача домашнего задания

## Репозиторий

Ссылка на GitHub-репозиторий с выполненным домашним заданием:

https://github.com/korn1loves/rag-homework

## Описание проекта

В рамках домашнего задания реализован учебный RAG-pipeline на основе датасета **SQuAD 2.0**.

Проект включает:

- подготовку данных;
- ingestion;
- chunking;
- построение TF-IDF индекса;
- retrieval;
- demo-answer с источниками;
- Streamlit UI;
- тесты;
- README с инструкцией запуска;
- отдельное описание данных в `doc/DATA.md`.

## Основные команды запуска

```bash
uv sync
uv run python scripts/build_index.py
uv run streamlit run app/main.py
```

## Проверка retrieval

```bash
uv run python scripts/check_retrieval.py
```

## Проверка demo-answer

```bash
uv run python scripts/check_generator.py
```

## Проверка тестов

```bash
uv run pytest tests/ -v
```

## Статус

Домашнее задание выполнено и готово к проверке.
