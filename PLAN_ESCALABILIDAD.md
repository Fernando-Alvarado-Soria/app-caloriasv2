# Plan Estrategico de Escalabilidad — CaloriasApp v2

> Documento vivo que describe el roadmap completo para llevar CaloriasApp de un proyecto personal a un producto escalable y profesional.

---

## Indice

1. [Vision y Objetivos](#vision-y-objetivos)
2. [Fase 0: Diagnostico y Estabilizacion](#fase-0-diagnostico-y-estabilizacion)
3. [Fase 1: ML — Entrenamiento Robusto y Profesional](#fase-1-ml--entrenamiento-robusto-y-profesional)
4. [Fase 2: Backend/API — Escalar Infraestructura](#fase-2-backendapi--escalar-infraestructura)
5. [Fase 3: App Kivy — UX y Funcionalidades](#fase-3-app-kivy--ux-y-funcionalidades)
6. [Fase 4: Escalabilidad y Producto](#fase-4-escalabilidad-y-producto)
7. [Cronograma Sugerido](#cronograma-sugerido)
8. [Metricas de Exito](#metricas-de-exito)
9. [Notas y Decisiones Pendientes](#notas-y-decisiones-pendientes)

---

## Vision y Objetivos

**Vision:** Convertir CaloriasApp en una aplicacion multiplataforma (Android/iOS/Web) que permita a cualquier usuario estimar calorias y macronutrientes a partir de una foto de comida, con un modelo de ML preciso, sincronizacion en la nube y experiencia de usuario profesional.

**Objetivos a 6 meses:**
- Modelo de clasificacion con >90% Top-1 accuracy (incluyendo comida mexicana)
- Backend escalable con autenticacion y base de datos PostgreSQL
- App Android funcional con inferencia on-device (TFLite)
- Sistema de usuarios con sincronizacion offline/online
- Tabla nutricional con 300+ alimentos

---

## Fase 0: Diagnostico y Estabilizacion

**Objetivo:** Dejar el repositorio en un estado limpio, reproducible y sin inconsistencias antes de agregar nuevas funcionalidades.

**Estado:** `PENDIENTE`

| # | Tarea | Prioridad | Estado |
|---|-------|-----------|--------|
| 0.1 | Revisar que `model_scripted.pt` y `metadata.json` esten sincronizados con el modelo en Railway | Alta | PENDIENTE |
| 0.2 | Verificar que version del modelo tiene Railway (v1 84.89%, v2 87.53%, o v3 mexicano) | Alta | PENDIENTE |
| 0.3 | Limpiar inconsistencias en `class_mapping.py` y `food_table.py` (clases que aparecen en metadata pero no tienen mapeo nutricional, duplicados, etc.) | Media | PENDIENTE |

**Criterio de salida:**
- `metadata.json`, `model_scripted.pt` y Railway estan sincronizados
- No hay clases sin mapeo nutricional
- El repo compila y corre sin errores

---

## Fase 1: ML — Entrenamiento Robusto y Profesional

**Objetivo:** Convertir el entrenamiento en un proceso reproducible, automatizado y sin friccion.

**Estado:** `PENDIENTE`

### Problemas identificados

1. **Desincronizacion Colab ↔ Repo local:** El modelo se entrena en Colab, se descarga en ZIP y se copia manualmente. Propenso a errores y olvidos.
2. **Codigo duplicado en notebook v3:** El training loop se copia inline en vez de reutilizar `ml/train.py`.
3. **Dataset se pierde al reiniciar runtime:** Food-101 (5GB) se descarga desde cero cada vez.
4. **No hay versionado de modelos:** Solo `best_model.pt` y `checkpoint_epoch2.pt`. No se saben que hiperparametros generaron cada modelo.
5. **No hay metricas de seguimiento:** No se guardan logs de entrenamiento para comparar corridas.
6. **Problema con `resume` desde `model_scripted.pt`:** El notebook v2 reconstruye `best_model.pt` extrayendo `state_dict()` de un modelo TorchScript. Esto es una anomalia porque TorchScript puede haber optimizado/eliminado ciertos estados (ej: batch norm running stats).

### Tareas

| # | Tarea | Descripcion | Impacto | Estado |
|---|-------|-------------|---------|--------|
| 1.1 | **Guardar checkpoints en Google Drive** | En lugar de descargar ZIP, guardar `best_model.pt` directamente en Drive con nombre versionado (`best_model_v2_87pt53.pt`). Asi Colab no pierde el modelo al reiniciar. | Alto | PENDIENTE |
| 1.2 | **Refactorizar notebook v3** | Reutilizar `ml/train.py` en vez de copiar el loop. Crear un script `train_mexican.py` que extienda `train.py` con logica de expansion de clases. | Alto | PENDIENTE |
| 1.3 | **Git LFS para modelos** | Usar Git LFS para versionar `best_model.pt` y `model_scripted.pt`. Elimina la necesidad de "descargar manualmente" desde Colab. | Medio | PENDIENTE |
| 1.4 | **Logging de entrenamiento** | Guardar `logs/training.csv` con epoca, train_loss, val_loss, val_acc, LR, tiempo. Facilita comparar corridas. | Medio | PENDIENTE |
| 1.5 | **Fix: `resume` desde checkpoint real** | Nunca reconstruir `best_model.pt` desde `model_scripted.pt`. Guardar `best_model.pt` completo en Drive durante cada entrenamiento. El `state_dict` de TorchScript puede ser incompleto. | Alto | PENDIENTE |
| 1.6 | **Descargar dataset Food-101 a Drive** | Montar Google Drive y descargar Food-101 a `/content/drive/MyDrive/food101/` para no re-descargar en cada sesion. | Alto | PENDIENTE |
| 1.7 | **Hiperparametros en YAML** | Crear `ml/config.yaml` con los parametros de cada version (v1, v2, v3). Permite versionar config y no depender de mutar `config.py` en runtime. | Medio | PENDIENTE |
| 1.8 | **Dataset mexicano en Colab** | Descargar/verificar que `ml/data/mexican_food/` tenga suficientes imagenes por clase (min 100). | Alto | PENDIENTE |
| 1.9 | **Entrenar modelo v3 mexicano** | Ejecutar notebook v3 con todas las mejoras anteriores, obtener modelo con 121 clases. | Alto | PENDIENTE |
| 1.10 | **Exportar y validar v3** | Exportar a TorchScript, probar localmente que predice mexicanas correctamente. | Alta | PENDIENTE |

**Orden de ejecucion recomendado:**
1. Implementar 1.5 (fix resume) + 1.1 (Drive checkpoints)
2. Implementar 1.6 (Drive dataset)
3. Implementar 1.2 (refactor v3)
4. Implementar 1.8 (dataset mexicano)
5. Entrenar 1.9 (modelo v3)
6. Implementar 1.4 (logs) + 1.7 (YAML config)
7. Implementar 1.10 (exportar y validar)

**Criterio de salida:**
- Modelo v3 entrenado con 121 clases, >85% Top-1
- Notebook v3 refactorizado y sin codigo duplicado
- Checkpoints guardados automaticamente en Drive
- Dataset Food-101 persistente en Drive

---

## Fase 2: Backend/API — Escalar Infraestructura

**Objetivo:** Convertir la API de Railway en un backend robusto con persistencia, autenticacion y CI/CD.

**Estado:** `PENDIENTE`

| # | Tarea | Descripcion | Prioridad | Estado |
|---|-------|-------------|-----------|--------|
| 2.1 | **PostgreSQL en Railway** | Railway ofrece PostgreSQL gratuito. Reemplazar SQLite por PostgreSQL en el servidor. Permite usuarios multiples y datos persistentes. | Alta | PENDIENTE |
| 2.2 | **Sistema de autenticacion (JWT)** | Crear endpoints `/register`, `/login`, `/me` con JWT. La app Kivy guarda el token y lo envia en cada request. | Alta | PENDIENTE |
| 2.3 | **Rate limiting + API Keys** | Proteger `/predict` con `slowapi` (limites por IP/token). Evitar abuso de la API publica. | Media | PENDIENTE |
| 2.4 | **Versionado de modelos en la API** | Endpoint `/predict` deberia aceptar `model_version` opcional. Permitir desplegar multiples versiones del modelo. | Media | PENDIENTE |
| 2.5 | **CI/CD (GitHub Actions)** | Automatizar deploy a Railway cuando se hace push a `main` con un modelo nuevo. | Media | PENDIENTE |
| 2.6 | **Logging de predicciones** | Guardar en DB cada prediccion: user_id, timestamp, imagen_hash, food_class, confidence. Util para analytics y debugging. | Media | PENDIENTE |
| 2.7 | **CORS restringido** | Cambiar `allow_origins=["*"]` a dominios especificos de la app. | Baja | PENDIENTE |

**Criterio de salida:**
- API con autenticacion JWT funcional
- PostgreSQL con tablas de usuarios y predicciones
- Rate limiting activo
- Deploy automatizado via GitHub Actions

---

## Fase 3: App Kivy — UX y Funcionalidades

**Objetivo:** Mejorar la experiencia de usuario para que sea una app realmente usable.

**Estado:** `PENDIENTE`

| # | Tarea | Descripcion | Prioridad | Estado |
|---|-------|-------------|-----------|--------|
| 3.1 | **Sistema de usuarios local** | En la app, opcion de "Iniciar sesion / Registrarse". Si no hay internet, funciona offline con SQLite local. | Alta | PENDIENTE |
| 3.2 | **Sincronizacion offline/online** | Cuando hay internet, sincronizar comidas locales al servidor. Resolver conflictos (ultima edicion gana). | Alta | PENDIENTE |
| 3.3 | **Editar/eliminar comidas del historial** | Anadir swipe-to-delete o boton de editar en cada fila del historial. | Alta | PENDIENTE |
| 3.4 | **Mostrar miniatura de imagen en historial** | En `history.kv`, mostrar `Image` con la foto que se guardo en `image_path`. | Media | PENDIENTE |
| 3.5 | **Mejorar selector de porcion** | Slider visual o stepper en vez de 3 botones. O usar una referencia visual (ej: moneda, mano) para estimar tamano. | Media | PENDIENTE |
| 3.6 | **Mejorar UI de prediccion** | Mostrar barras de progreso o badges de confianza. Si confidence < 60%, mostrar warning al usuario. | Media | PENDIENTE |
| 3.7 | **Dark mode / temas** | Kivy permite themes. Implementar toggle en settings. | Baja | PENDIENTE |
| 3.8 | **Notificaciones diarias** | "Ya registraste tu almuerzo?" usando `plyer.notification`. | Baja | PENDIENTE |
| 3.9 | **Pantalla de Settings/Perfil** | Nombre, meta calorias diaria, objetivo (perder peso, mantener, ganar). | Media | PENDIENTE |
| 3.10 | **Estadisticas semanales/mensuales** | Graficas de barras/pie con distribucion de macros en el tiempo. | Media | PENDIENTE |

**Criterio de salida:**
- App con login/logout funcional
- Historial editable con imagenes
- Sincronizacion automatica cuando hay conexion
- Settings con metas personales

---

## Fase 4: Escalabilidad y Producto

**Objetivo:** Preparar la app para produccion y multiples plataformas.

**Estado:** `PENDIENTE`

| # | Tarea | Descripcion | Prioridad | Estado |
|---|-------|-------------|-----------|--------|
| 4.1 | **On-device inference (TFLite)** | Convertir a ONNX o TFLite para que el modelo corra en Android sin depender de internet. EfficientNet-B0 tiene ~5M parametros, cabe en movil. | Alta | PENDIENTE |
| 4.2 | **Empaquetar para Android (Buildozer)** | Crear `buildozer.spec` y probar APK en dispositivo real. | Alta | PENDIENTE |
| 4.3 | **Mejorar tabla nutricional** | Agregar mas alimentos (hasta ~300). Considerar integrar API de USDA real. | Media | PENDIENTE |
| 4.4 | **Estimacion de peso por volumen** | Estrategia visual: detectar plato en la imagen y estimar tamano relativo para calcular gramos automaticamente. | Alta (complejo) | PENDIENTE |
| 4.5 | **Dashboard web** | Pequena web app donde el usuario vea estadisticas de su semana/mes. | Media | PENDIENTE |
| 4.6 | **Internacionalizacion** | Soporte para ingles/espanol. | Baja | PENDIENTE |
| 4.7 | **Tests automatizados** | Tests unitarios para DB, inference, API. Tests de integracion para el pipeline ML. | Media | PENDIENTE |
| 4.8 | **Documentacion API publica** | Swagger/OpenAPI con ejemplos para desarrolladores terceros. | Baja | PENDIENTE |

**Criterio de salida:**
- APK funcional en Android
- Inferencia on-device con TFLite
- Dashboard web con estadisticas
- Tests automatizados pasando

---

## Cronograma Sugerido

| Semana | Foco | Entregable |
|--------|------|------------|
| Semana 1 | Fase 0 + Fase 1 (ML fix) | Repo estabilizado, notebook v3 refactorizado, checkpoints en Drive |
| Semana 2 | Fase 1 (ML train) | Modelo v3 mexicano entrenado y exportado |
| Semana 3 | Fase 2 (Backend) | PostgreSQL + JWT + API segura |
| Semana 4 | Fase 3 (App) | Login, sync offline, editar historial |
| Semana 5 | Fase 3 (App UX) | Miniaturas, settings, estadisticas |
| Semana 6 | Fase 4 (Producto) | TFLite, Buildozer, APK funcional |
| Semana 7+ | Iteracion | Mejoras continuas, mas alimentos, dashboard web |

---

## Metricas de Exito

| Metrica | Actual | Objetivo 3 meses | Objetivo 6 meses |
|---------|--------|------------------|-----------------|
| Top-1 Accuracy | 87.53% (101 clases) | 90% (121 clases) | 92%+ (150+ clases) |
| Modelo local en Android | No | TFLite funcional | Optimizado (<50MB) |
| Usuarios soportados | 0 (sin auth) | 100+ | 1000+ |
| Alimentos en tabla | 78 | 150 | 300+ |
| Tiempo de inferencia API | ~2s | <1s | <500ms |
| Tiempo de inferencia local | N/A | <3s | <1s |
| Cobertura de tests | 0% | 30% | 60% |

---

## Notas y Decisiones Pendientes

- **Railway modelo actual:** Se desconoce si tiene v1 (84.89%), v2 (87.53%) o v3 mexicano. Verificar en Fase 0.
- **Offline-first vs online-first:** Pendiente decision del usuario. Cambia la arquitectura radicalmente.
- **Presupuesto infraestructura:** Railway gratuito vs plan pago. Si es MVP, gratuito es suficiente.
- **Stack multiplataforma:** Kivy es rapido para prototipar pero limitado. Si el objetivo es startup real, evaluar Flutter o React Native a futuro.
- **Dataset mexicano:** `ml/collect_images.py` existe pero no hay datos locales. Evaluar si las imagenes descargadas de DuckDuckGo tienen calidad suficiente o se necesita un dataset curado.

---

## Historial de Cambios

| Fecha | Autor | Cambio |
|-------|-------|--------|
| 2026-06-06 | OpenCode | Creacion inicial del plan |

