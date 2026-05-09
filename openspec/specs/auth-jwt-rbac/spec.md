# Delta Specs — Change-01-Auth-JWT-RBAC

Auth + RBAC completo con JWT de doble token (access 30min, refresh 7d), rotación con replay detection, y 4 roles RBAC.

---

## Capability: auth-register

### Description
Registro de nuevo usuario. Crea un `Usuario` con rol `CLIENT` automáticamente y devuelve un par de tokens.

### Dependencies
- `security-utils` (hashing + JWT + refresh token)

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-REG-01 | MUST asignar rol CLIENT automáticamente, nunca del request | RN-AU07, US-001 |
| REQ-REG-02 | MUST verificar unicidad de email antes de crear | RN-DA04, US-001 |
| REQ-REG-03 | MUST rechazar password < 8 chars con 422 | US-001 |
| REQ-REG-04 | MUST rechazar nombre/apellido < 2 o > 80 chars con 422 | RN schema RegisterRequest |
| REQ-REG-05 | MUST devolver 201 + TokenResponse en éxito | US-001 |
| REQ-REG-06 | MUST devolver 409 si email ya registrado | US-001 |

### Scenarios

#### REG-01: Registro exitoso
- **Given** un email y password válidos no registrados
- **When** POST `/api/v1/auth/register` con `{nombre, apellido, email, password}`
- **Then** respuesta 201 con `TokenResponse` (access_token, refresh_token, token_type="bearer", expires_in=1800)
- **And** usuario creado con rol CLIENT, password hasheado con bcrypt cost≥12

#### REG-02: Email duplicado
- **Given** un email ya registrado
- **When** POST `/api/v1/auth/register` con ese email
- **Then** respuesta 409, code="CONFLICT", detail="El email ya está registrado"

#### REG-03: Password débil
- **Given** password de 6 caracteres
- **When** POST `/api/v1/auth/register`
- **Then** respuesta 422, code="VALIDATION_ERROR", field="password"

#### REG-04: Campos faltantes
- **Given** body sin campo `nombre`
- **When** POST `/api/v1/auth/register`
- **Then** respuesta 422 con error de validación Pydantic

---

## Capability: auth-login

### Description
Autentica credenciales, devuelve access + refresh token. No diferencia "email no existe" de "password incorrecta" (RN-AU08). Rate limited 5 intentos/15min por IP.

### Dependencies
- `security-utils`
- `refresh-token-storage` (generar y persistir refresh token)

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-LOG-01 | MUST devolver 200 + TokenResponse para credenciales válidas | US-002 |
| REQ-LOG-02 | MUST devolver 401 para credenciales inválidas (mensaje genérico, sin revelar si email existe) | RN-AU08, US-002 |
| REQ-LOG-03 | MUST devolver 401 si `activo=False` | US-002 |
| REQ-LOG-04 | MUST rate limit: 5 intentos/15min por IP, 429 + Retry-After header | RN-AU06, US-073 |
| REQ-LOG-05 | MUST generar access token JWT (HS256) con sub=user_id, email, roles, exp | RN-AU02 |
| REQ-LOG-06 | MUST generar refresh token UUIDv4 y almacenar hash SHA-256 en BD | RN-AU03 |

### Scenarios

#### LOG-01: Login exitoso
- **Given** usuario registrado con email válido y password correcto, activo=True
- **When** POST `/api/v1/auth/login` con `{email, password}`
- **Then** respuesta 200 con `TokenResponse`
- **And** refresh token almacenado en tabla `refresh_tokens` con token_hash SHA-256, revoked_at=NULL

#### LOG-02: Email inexistente
- **Given** email no registrado
- **When** POST `/api/v1/auth/login`
- **Then** respuesta 401, detail="Email o contraseña incorrectos"

#### LOG-03: Password incorrecto
- **Given** email registrado pero password incorrecto
- **When** POST `/api/v1/auth/login`
- **Then** respuesta 401, detail="Email o contraseña incorrectos" (mismo mensaje que LOG-02)

#### LOG-04: Cuenta deshabilitada
- **Given** usuario con activo=False
- **When** POST `/api/v1/auth/login` con credenciales correctas
- **Then** respuesta 401, detail="Cuenta deshabilitada"

#### LOG-05: Rate limit excedido
- **Given** 5 intentos fallidos desde misma IP en ventana de 15 minutos
- **When** 6to intento de login
- **Then** respuesta 429, code="RATE_LIMIT_EXCEEDED", header Retry-After presente

---

## Capability: auth-refresh

### Description
Rota el par de tokens: revoca el refresh token anterior, emite uno nuevo. Detecta replay attack (RN-AU05): si un token ya revocado se reusa, revoca TODOS los tokens del usuario.

### Dependencies
- `security-utils`
- `refresh-token-storage`

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-REF-01 | MUST rotar tokens: revocar anterior, emitir nuevo par | RN-AU04, US-003 |
| REQ-REF-02 | MUST responder 401 si refresh token expirado | US-003 |
| REQ-REF-03 | MUST detectar replay: si token ya revocado, revocar TODOS los tokens del usuario y responder 401 | RN-AU05, US-003 |
| REQ-REF-04 | MUST responder 401 si token no existe en BD | US-003 |
| REQ-REF-05 | MUST emitir nuevo refresh token con expiración 7d desde emisión | RN-AU03 |

### Scenarios

#### REF-01: Refresh exitoso con rotación
- **Given** refresh token válido y no expirado, activo en BD
- **When** POST `/api/v1/auth/refresh` con `{refresh_token}`
- **Then** respuesta 200 con nuevo `TokenResponse`
- **And** refresh token anterior marcado con revoked_at en BD
- **And** nuevo refresh token almacenado con nuevo hash

#### REF-02: Refresh token expirado
- **Given** refresh token con expires_at en pasado
- **When** POST `/api/v1/auth/refresh`
- **Then** respuesta 401, code="UNAUTHORIZED"

#### REF-03: Replay attack detectado
- **Given** refresh token ya revocado (replay)
- **When** POST `/api/v1/auth/refresh` con ese token
- **Then** respuesta 401
- **And** TODOS los refresh tokens del usuario (no expirados) se marcan como revoked_at

#### REF-04: Token inexistente
- **Given** refresh token con hash no encontrado en BD
- **When** POST `/api/v1/auth/refresh`
- **Then** respuesta 401, code="UNAUTHORIZED"

---

## Capability: auth-logout

### Description
Cierra la sesión del usuario. Revoca el refresh token en BD marcando `revoked_at`. El access token sigue válido hasta su expiración natural (stateless).

### Dependencies
- `refresh-token-storage`

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-LOGOUT-01 | MUST revocar refresh token en BD (set revoked_at) | US-004 |
| REQ-LOGOUT-02 | MUST responder 204 No Content en éxito | US-004 |
| REQ-LOGOUT-03 | MUST requerir Bearer token (autenticación) | US-004 |
| REQ-LOGOUT-04 | SHOULD responder 401 si refresh token no existe o ya revocado | RN-RB10 |

### Scenarios

#### LOGOUT-01: Logout exitoso
- **Given** usuario autenticado con refresh token activo
- **When** POST `/api/v1/auth/logout` con `{refresh_token}` + Bearer token
- **Then** respuesta 204 No Content
- **And** refresh token tiene revoked_at seteado en BD

#### LOGOUT-02: Refresh token ya revocado
- **Given** refresh token ya con revoked_at seteado
- **When** POST `/api/v1/auth/logout`
- **Then** respuesta 401, code="UNAUTHORIZED"

#### LOGOUT-03: Sin autenticación
- **Given** request sin Bearer token
- **When** POST `/api/v1/auth/logout`
- **Then** respuesta 401, code="UNAUTHORIZED"

---

## Capability: auth-me

### Description
Devuelve los datos del usuario autenticado: id, nombre, apellido, email, roles, created_at. Nunca expone password_hash.

### Dependencies
- `rbac-authorization` (get_current_user)

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-ME-01 | MUST devolver 200 + UserResponse para token válido | US-061 |
| REQ-ME-02 | MUST incluir id, nombre, apellido, email, roles, created_at | schema UserResponse |
| REQ-ME-03 | MUST NUNCA incluir password_hash | RN schema |
| REQ-ME-04 | MUST devolver 401 si falta token o es inválido | RN-RB10 |

### Scenarios

#### ME-01: Usuario autenticado
- **Given** usuario con token JWT válido
- **When** GET `/api/v1/auth/me` con header `Authorization: Bearer <token>`
- **Then** respuesta 200 con `UserResponse`
- **And** roles incluye lista de códigos (ej: ["CLIENT"])

#### ME-02: Sin token
- **Given** request sin Authorization header
- **When** GET `/api/v1/auth/me`
- **Then** respuesta 401, code="UNAUTHORIZED"

#### ME-03: Token expirado
- **Given** JWT expirado
- **When** GET `/api/v1/auth/me`
- **Then** respuesta 401, code="UNAUTHORIZED"

---

## Capability: rbac-authorization

### Description
Dos dependencias FastAPI: `get_current_user()` (decodifica JWT, carga usuario de BD, 401 si falla) y `require_role(roles)` (valida roles del JWT contra lista permitida, 403 si no alcanza).

### Dependencies
- `security-utils`

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-RBAC-01 | MUST extraer token de header `Authorization: Bearer <token>` | RN-RB10 |
| REQ-RBAC-02 | MUST decodificar y validar JWT (firma HS256, exp) | RN-AU02, US-006 |
| REQ-RBAC-03 | MUST cargar usuario fresco de BD por user_id del JWT | US-006 |
| REQ-RBAC-04 | MUST devolver 401 si token faltante, inválido, expirado, o usuario deshabilitado | RN-RB10 |
| REQ-RBAC-05 | `require_role` MUST devolver 403 si usuario no tiene rol requerido | RN-RB09, US-006 |
| REQ-RBAC-06 | `require_role` MUST permitir lista de roles (OR lógico) | US-006 |
| REQ-RBAC-07 | `require_role` MUST leer roles del JWT (no consulta BD) | proposal |
| REQ-RBAC-08 | MUST exponer `get_current_user` y `require_role` en `app/dependencies.py` | proposal |

### Scenarios

#### RBAC-01: Token válido devuelve usuario
- **Given** JWT válido con sub=1
- **When** se ejecuta `get_current_user`
- **Then** retorna instancia de Usuario con id=1

#### RBAC-02: Token faltante
- **Given** request sin Authorization header
- **When** se ejecuta `get_current_user`
- **Then** HTTPException 401, code="UNAUTHORIZED"

#### RBAC-03: Token expirado
- **Given** JWT con exp en pasado
- **When** se ejecuta `get_current_user`
- **Then** HTTPException 401, code="UNAUTHORIZED"

#### RBAC-04: Rol suficiente pasa
- **Given** usuario con rol ADMIN en JWT
- **When** `require_role(["ADMIN"])` se ejecuta
- **Then** no lanza excepción (pass)

#### RBAC-05: Rol insuficiente
- **Given** usuario con rol CLIENT en JWT
- **When** `require_role(["ADMIN"])` se ejecuta
- **Then** HTTPException 403, code="FORBIDDEN"

---

## Capability: security-utils

### Description
Módulo utilitario `app/security.py` con funciones puras: hashing bcrypt (cost≥12), creación/decodificación JWT (HS256), generación de refresh tokens UUIDv4 y hash SHA-256.

### Dependencies
- Ninguna (utilitario puro)

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-SEC-01 | MUST hashear password con bcrypt cost≥12 | RN-AU01, US-001 |
| REQ-SEC-02 | MUST verificar password contra hash con bcrypt | RN-AU01 |
| REQ-SEC-03 | MUST crear JWT HS256 con sub=user_id, email, roles, exp, iat | RN-AU02 |
| REQ-SEC-04 | MUST decodificar JWT validando firma y exp | RN-AU02 |
| REQ-SEC-05 | MUST generar refresh token como UUID v4 | RN-AU03 |
| REQ-SEC-06 | MUST hashear refresh token con SHA-256 para almacenamiento | RN-AU03 |
| REQ-SEC-07 | MUST usar SECRET_KEY de settings para firmar JWT | config.py |

### Scenarios

#### SEC-01: Hash y verify exitoso
- **Given** password "Test1234!"
- **When** se hashea y luego se verifica
- **Then** verify retorna True
- **And** hash es string de 60 caracteres (formato bcrypt)

#### SEC-02: Verify con password incorrecto
- **Given** hash de "passA"
- **When** se verifica "passB"
- **Then** verify retorna False

#### SEC-03: JWT create y decode
- **Given** payload `{sub: 1, email: "a@b.com", roles: ["CLIENT"]}`
- **When** se crea JWT y luego se decodifica
- **Then** decode retorna payload original con exp e iat

#### SEC-04: Token manipulado
- **Given** JWT válido
- **When** se modifica el payload (firma inválida)
- **Then** decode lanza error JWTError

#### SEC-05: Token expirado
- **Given** JWT con exp en pasado
- **When** se decodifica
- **Then** decode lanza error por expiración
