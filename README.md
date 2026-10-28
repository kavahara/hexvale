# hexvale

Сайт студии Hexvale — https://hexvale.dev. Чистый HTML + CSS без сборки, JavaScript — два маленьких файла; публикуется GitHub Pages из корня ветки `main`.

| Путь | Страница |
|---|---|
| `/`, `/ru/` | Главная студии (EN / RU) |
| `/orlo/`, `/ru/orlo/` | Orlo — сканер документов для iPhone |
| `/orlo/privacy/`, `/ru/orlo/privacy/` | Политика конфиденциальности Orlo |
| `/orlo/support/`, `/ru/orlo/support/` | Поддержка Orlo |
| `/fitness/`, `/ru/fitness/` | Фитнес-приложение — заглушка «Coming soon» |
| `/privacy/`, `/ru/privacy/` | Общая политика студии |

Стили — `assets/site.css`: нейтральная палитра студии, палитры продуктов — классы `pal-orlo` и `pal-fitness`. Светлая и тёмная тема — по `prefers-color-scheme`, кнопка в шапке переключает их вручную (`assets/theme.js`, выбор хранится в `localStorage` этого браузера; тёмные правила в CSS написаны парой: по системе и для `data-theme="dark"`). На странице Orlo блок «Размер под задачу» живой: ползунок качества и готовые настройки меняют оценку размера (`assets/orlo-meter.js`). Телефон и лист с уголками нарисованы на CSS, фотографии и керамика — `assets/img/` (у картинок со светлой и тёмной версией классы `img-light` / `img-dark`); анимации отключаются при «Уменьшении движения». Знак Hexvale — `assets/logo/hexvale-mark.svg` (в шапке подставляется маской и берёт цвет текста); иконка Orlo — `assets/orlo/icon.svg`, слово «Orlo» встроено в страницы как SVG. Значки сайта — `assets/favicon.svg`, `assets/favicon-32.png`, `assets/apple-touch-icon.png`; превью для ссылок — `assets/og/`.

Посмотреть локально (ссылки от корня, поэтому нужен сервер, а не открытие файла):

```bash
python3 -m http.server 8000
```

Проверить ссылки между страницами, canonical, EN/RU-пары и переключатель языка:

```bash
python3 scripts/check_links.py
```
