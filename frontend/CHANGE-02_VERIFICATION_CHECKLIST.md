# 🧪 Lista de Verificación Manual — Change 02 REAL: Layout + Navigation

> **Instrucciones**: Arrancá el frontend con `cd frontend && npm run dev`, abrí `http://localhost:5173`, y seguí cada prueba.

## 1. Smoke Test — App Arranca ✅

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 1.1 | Abrir `http://localhost:5173` | Ver el HomePage con hero gradient y cards de features |
| 1.2 | Verificar que NO hay errores en console (F12 → Console) | Sin errores rojos |

## 2. Navegación como Usuario No Autenticado 🚶

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 2.1 | Ver el Header | Logo "Food Store" + nav links: Catálogo, Iniciar Sesión, Registrarse |
| 2.2 | Hacer clic en "Catálogo" | Navega a `/productos` — ver "Próximamente" |
| 2.3 | Hacer clic en "Iniciar Sesión" | Navega a `/auth/login` — ver formulario de login |
| 2.4 | Hacer clic en "Registrarse" | Navega a `/auth/register` — ver formulario de registro |
| 2.5 | Ir a una ruta inexistente (`/no-existe`) | Ver página 404 con "Volver al inicio" |
| 2.6 | Ir a `/admin` directamente | Redirige a `/auth/login?redirect=/admin` |

## 3. Registro de Usuario 📝

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 3.1 | Completar registro con datos válidos (nombre, apellido, email@test.com, contraseña 8+ chars) | Redirige a Home, aparece el UserDropdown con el nombre del usuario |
| 3.2 | Verificar que en Header ahora aparece el avatar + nombre | ✅ |
| 3.3 | Cerrar sesión (UserDropdown → "Cerrar Sesión") | Redirige a Home, Header vuelve a mostrar "Iniciar Sesión" |

## 4. Login de Usuario 🔑

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 4.1 | Ir a `/auth/login` | Ver formulario con email + password |
| 4.2 | Login con credenciales inválidas | Ver mensaje de error (rojo) |
| 4.3 | Login con el admin: `admin@foodstore.com` / `Admin1234!` | Redirige a Home, user dropdown muestra "admin@foodstore.com" |
| 4.4 | **CRÍTICO**: Refrescar la página (F5) | NO redirige a login — la sesión persiste gracias al persist middleware |
| 4.5 | Verificar que el menú cambió para ADMIN | Deberías ver más opciones: Dashboard, Usuarios, Productos, etc. |

## 5. Navegación por Rol 👑

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 5.1 | Login como ADMIN (`admin@foodstore.com`) | Menú muestra: Catálogo, Dashboard, Productos, Categorías, Pedidos, Usuarios, Stock |
| 5.2 | Ir a `/admin` | Ver "Dashboard — Próximamente" (placeholder, implementación futura) |
| 5.3 | Ir a `/carrito` | Ver "Carrito — Próximamente" |
| 5.4 | Ir a `/perfil` | Ver "Mi Perfil — Próximamente" |
| 5.5 | **PRUEBA DE SEGURIDAD**: Ir a `/productos/123` | Ver "Detalle del Producto — Próximamente" (ruta pública, sin auth) |

## 6. Responsive / Mobile 📱

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 6.1 | Abrir DevTools → toggle device toolbar (Ctrl+Shift+M) | Ver el layout adaptado |
| 6.2 | En tamaño mobile (< 768px) | El menú horizontal desaparece, aparece el icono hamburguesa (☰) |
| 6.3 | Click en hamburguesa | Se abre un menú slide-in desde la izquierda con overlay |
| 6.4 | Click en un item del menú | El menú se cierra y navega a la ruta |
| 6.5 | Click en el overlay (fuera del menú) | El menú se cierra |
| 6.6 | En desktop (> 768px) | Menú horizontal visible, sin hamburguesa |

## 7. Breadcrumbs 🍞

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 7.1 | Ir a `/productos/123` | Breadcrumbs: "Inicio > Productos > Detalle" |
| 7.2 | Ir a `/admin/usuarios` | Breadcrumbs: "Inicio > Administración > Usuarios" |
| 7.3 | Ir a `/` | Breadcrumbs NO se muestran (oculto en homepage) |

## 8. Error Handling 🛡️

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 8.1 | Ir a `/no-existe` | Página 404 con "Volver al inicio" |
| 8.2 | Ir a `/admin` sin ser ADMIN | Página 403 "No tenés permisos" |
| 8.3 | **PRUEBA DE TOAST**: Sin conexión al backend, intentar login | Ver toast de error: "Error interno, intentá de nuevo más tarde" |

## 9. Dark Mode 🌗

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 9.1 | Click en el toggle de tema (🌙/☀️) | El sitio cambia a dark mode |
| 9.2 | Refrescar la página | El tema persiste (guardado en uiStore) |
| 9.3 | Volver a clickear | Vuelve a light mode |

## 10. UserDropdown 👤

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 10.1 | Login como admin | Ver avatar circular con inicial del nombre |
| 10.2 | Click en el avatar | Dropdown se abre: nombre, email, "Mi Perfil", "Cerrar Sesión" |
| 10.3 | Click fuera del dropdown | Se cierra |
| 10.4 | Click en "Cerrar Sesión" | Redirige a Home, menu vuelve a estado no autenticado |

## 🔍 Pruebas de API (desde Swagger / DevTools Network)

Si querés verificar el backend también, abrí `http://localhost:8000/docs` y:

| # | Prueba | Resultado esperado |
|---|--------|-------------------|
| 11.1 | `POST /api/v1/auth/login` con admin@foodstore.com | 200 + tokens + user con roles: ["ADMIN"] |
| 11.2 | `POST /api/v1/auth/register` con nuevo email | 201 + tokens + user con roles: ["CLIENT"] |
| 11.3 | `POST /api/v1/auth/refresh` con refresh_token | 200 + nuevo par de tokens |
| 11.4 | `POST /api/v1/auth/logout` con token | 204 No Content |
| 11.5 | `GET /api/v1/categorias` (sin auth) | 200 + árbol de categorías |

---

## 📊 Resumen de Resultados

| Sección | Tests | ✅ Pasaron | ❌ Fallaron |
|---------|-------|-----------|------------|
| Smoke Test | 2 | — | — |
| Navegación Anónimo | 6 | — | — |
| Registro | 3 | — | — |
| Login | 5 | — | — |
| Navegación por Rol | 5 | — | — |
| Responsive | 6 | — | — |
| Breadcrumbs | 3 | — | — |
| Error Handling | 3 | — | — |
| Dark Mode | 3 | — | — |
| UserDropdown | 4 | — | — |
| API Tests | 5 | — | — |
| **TOTAL** | **45** | **0** | **0** |

> Copiá esta checklist a un archivo e iba marcando con ✅ a medida que probás.
> Si encontrás algún error (como pasó con categorías en Swagger), **anotá el paso exacto** y decime para fixearlo.
