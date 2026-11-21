# Okno na świat

Telefon albo laptop jako szyba okna. Przednia kamera śledzi oczy (MediaPipe Face Landmarker), a krajobraz za oknem rysuje się z perspektywą sprzężoną z pozycją głowy (head-coupled perspective). Bliska trawa przesuwa się szybko, drzewa wolniej, góry i chmury prawie wcale, więc widok ma prawdziwą głębię.

Strona: https://jakolsky.github.io/okno_na_swiat/

## Co jest w środku
- `index.html`: scena i śledzenie oczu
- `img/`: panorama rozcięta na warstwy: niebo z górami, dolina z wioską, łąka (krojona na ok. 45 pasów o rosnącej głębi), stodoła, jabłoń i dwa domy po bokach okna
- `zrodlo/panorama.png`: oryginalna panorama
- `tools/build_layers.py`: skrypt, który tnie panoramę na warstwy (`python3 tools/build_layers.py`)
- `model/face_landmarker.task`: model twarzy MediaPipe (float16, v1), wbudowany w projekt
- `mediapipe/`: biblioteka `@mediapipe/tasks-vision` 0.10.14 (JS i WASM), wbudowana w projekt

Strona nie pobiera niczego z zewnętrznych CDN poza fontami, więc działa też tam, gdzie CDN są blokowane.

## Sterowanie
- przycisk „⇄ kierunek”: przełącza między odwróconą perspektywą a zachowaniem prawdziwej szyby
- suwak „Siła głębi” na ekranie startowym
- podgląd kamery w rogu pokazuje, czy twarz jest wykryta; stuknij, żeby go przyciemnić
- bez kamery: przeciąganie palcem, myszą albo przechylanie telefonu

## Prywatność
Obraz z kamery jest analizowany wyłącznie lokalnie w przeglądarce. Nic nie jest wysyłane ani zapisywane.

## Licencje
MediaPipe i model Face Landmarker: Apache License 2.0, © Google LLC (zob. `mediapipe/LICENSE`).
