# hexvale

Сайт студии Hexvale — https://hexvale.dev. Чистый HTML + CSS, без сборки и JavaScript; публикуется GitHub Pages из корня ветки `main`.

| Путь | Страница |
|---|---|
| `/`, `/ru/` | Главная студии (EN / RU) |
| `/orlo/`, `/ru/orlo/` | Orlo — сканер документов для iPhone |
| `/orlo/privacy/`, `/ru/orlo/privacy/` | Политика конфиденциальности Orlo |
| `/orlo/support/`, `/ru/orlo/support/` | Поддержка Orlo |
| `/fitness/`, `/ru/fitness/` | Фитнес-приложение — заглушка «Coming soon» |
| `/privacy/`, `/ru/privacy/` | Общая политика студии |

Стили — `assets/site.css`: нейтральная палитра студии, акценты продуктов — классы `t-orlo` и `t-fitness`, тёплая палитра страниц Orlo — `page-orlo`. Светлая и тёмная тема — по `prefers-color-scheme`.

Посмотреть локально (ссылки от корня, поэтому нужен сервер, а не открытие файла):

```bash
python3 -m http.server 8000
```

Проверить ссылки между страницами, canonical, EN/RU-пары и переключатель языка:

```bash
python3 scripts/check_links.py
```
