---
name: be-best-practices
description: >
  Backend best practices for Node.js + Zod + Prisma + PostgreSQL + MongoDB + Redis teams.
  Organized by concern: request validation, PostgreSQL/Prisma patterns, MongoDB patterns,
  Redis caching, error handling, API design, TypeScript, and file structure.
  Auto-loads in every backend dev session.
triggers:
  - backend
  - Node.js
  - API
  - Prisma
  - PostgreSQL
  - MongoDB
  - Redis
  - Zod
  - be best practices
---

# Backend Best Practices

These are the backend standards for this team's stack: Node.js + Zod + Prisma + PostgreSQL + MongoDB + Redis.
Apply these in every backend dev session. When a developer asks "how should I do X?", answer from these practices first.

---

## 1. Request Validation

**Rule: Zod at every route entry point. Validate before any business logic runs.**

**Required pattern:**
```typescript
// Define schema in src/schemas/
export const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(['admin', 'user', 'viewer']),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;

// Validate at route handler — before service call
router.post('/users', async (req, res, next) => {
  const result = createUserSchema.safeParse(req.body);

  if (!result.success) {
    return next(new ValidationError(result.error.flatten()));
  }

  const user = await userService.create(result.data); // typed as CreateUserInput
  res.status(201).json({ data: user });
});
```

**Anti-patterns:**
- Passing `req.body` directly to services without validation
- Defining TypeScript types separately from Zod schemas — always `z.infer<>`
- Using `.parse()` in route handlers — use `.safeParse()` and handle errors explicitly
- Validating inside the service layer — validate at the route, trust data downstream

---

## 2. Database — PostgreSQL (Prisma)

**Rule: all DB access through repository classes. Prisma never called in routes or services.**

**Repository pattern:**
```typescript
// src/repositories/user.repository.ts
export class UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({
      where: { id },
      select: {        // always select explicitly — never return *
        id: true,
        email: true,
        name: true,
        createdAt: true,
      },
    });
  }

  async create(data: CreateUserInput): Promise<User> {
    return this.prisma.user.create({
      data,
      select: { id: true, email: true, name: true, createdAt: true },
    });
  }
}
```

**Transactions:**
```typescript
// Multi-step writes always use transactions
async transferCredits(fromId: string, toId: string, amount: number) {
  return this.prisma.$transaction(async (tx) => {
    await tx.wallet.update({ where: { userId: fromId }, data: { balance: { decrement: amount } } });
    await tx.wallet.update({ where: { userId: toId }, data: { balance: { increment: amount } } });
  });
}
```

**Anti-patterns:**
- `prisma.user.findMany()` without `select` — always specify fields
- Prisma calls in route handlers or service files
- `prisma.$queryRaw` without a documented reason
- N+1 queries — use `include` or batch with `findMany({ where: { id: { in: ids } } })`

---

## 3. Database — MongoDB

**Rule: Mongoose schemas required. No schemaless writes. Mirror with Zod.**

**Schema setup:**
```typescript
// src/models/product.model.ts
const productSchema = new mongoose.Schema({
  name: { type: String, required: true, maxlength: 200 },
  price: { type: Number, required: true, min: 0 },
  categoryId: { type: mongoose.Schema.Types.ObjectId, ref: 'Category' },
  metadata: { type: Map, of: String }, // typed even for flexible fields
}, { timestamps: true });

export const Product = mongoose.model('Product', productSchema);

// Mirror with Zod for API validation
export const productInputSchema = z.object({
  name: z.string().max(200),
  price: z.number().min(0),
  categoryId: z.string(),
  metadata: z.record(z.string()).optional(),
});
```

**Read patterns:**
```typescript
// Use lean() for read-only queries — skips Mongoose document overhead
const products = await Product.find({ categoryId }).lean();

// Projection — only return needed fields
const names = await Product.find({}).select('name price').lean();
```

**Anti-patterns:**
- Writing to MongoDB without a Mongoose schema
- Storing arbitrary JSON blobs — define the shape in the schema
- Using `.find()` without `.lean()` for read-only operations
- No indexes — define indexes in schema for all queried fields

---

## 4. Caching — Redis

**Rule: cache-aside pattern. Always set TTL. Invalidate on write.**

**Cache-aside pattern:**
```typescript
// src/repositories/user.repository.ts
async findById(id: string): Promise<User | null> {
  const cacheKey = `user:${id}:profile`;

  // 1. Check cache
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // 2. Cache miss — query DB
  const user = await this.prisma.user.findUnique({
    where: { id },
    select: { id: true, email: true, name: true },
  });

  // 3. Write to cache with TTL
  if (user) {
    await redis.setex(cacheKey, 3600, JSON.stringify(user)); // 1 hour TTL
  }

  return user;
}

// Invalidate on write
async update(id: string, data: UpdateUserInput): Promise<User> {
  const user = await this.prisma.user.update({
    where: { id },
    data,
    select: { id: true, email: true, name: true },
  });
  await redis.del(`user:${id}:profile`); // clear cache on update
  return user;
}
```

**Key naming convention:**
```
[entity]:[id]:[scope]
user:123:profile
user:123:permissions
session:abc-xyz
rate-limit:ip:192.168.1.1
```

**Anti-patterns:**
- Redis keys without TTL — always use `setex` or `expire`
- Using Redis as primary data store — it's a cache, not a database
- Not invalidating cache on mutations — leads to stale data
- Storing large objects in Redis — keep values small, store IDs not full documents

**Redis use cases:**
- Session storage
- Rate limiting
- Pub/sub for real-time events
- Distributed locks
- Short-lived tokens (email verification, password reset)

---

## 5. Error Handling

**Rule: structured error classes, central middleware, never expose internals.**

**Error class setup:**
```typescript
// src/lib/errors.ts
export class AppError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code: string,
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(public details: unknown) {
    super('Validation failed', 400, 'VALIDATION_ERROR');
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

export class UnauthorizedError extends AppError {
  constructor() {
    super('Unauthorized', 401, 'UNAUTHORIZED');
  }
}
```

**Central error middleware (Express):**
```typescript
// src/middleware/error.middleware.ts
export function errorMiddleware(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction,
) {
  logger.error({ err, path: req.path, method: req.method }); // full error logged internally

  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message },
    });
  }

  // Unknown error — never expose details
  res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' },
  });
}
```

**HTTP status codes:**
| Code | When |
|------|------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error / bad request |
| 401 | Not authenticated |
| 403 | Authenticated but not permitted |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state mismatch) |
| 422 | Unprocessable (semantic validation) |
| 500 | Unhandled server error |

**Anti-patterns:**
- `throw new Error('User not found')` — use `NotFoundError('User')`
- Returning error details from 500 responses — log internally, return generic message
- try/catch in every function — only catch what you can handle, let the rest bubble to middleware
- `res.status(200).json({ success: false, error: '...' })` — use correct HTTP status codes

---

## 6. API Design

**Rule: consistent response shape, REST conventions, always versioned.**

**Response envelope:**
```typescript
// Success
{ "data": { ... }, "meta": { "page": 1, "total": 42 } }

// Error (handled by error middleware)
{ "error": { "code": "NOT_FOUND", "message": "User not found" } }

// Collection
{ "data": [...], "meta": { "page": 1, "limit": 20, "total": 100, "cursor": "abc" } }
```

**REST conventions:**
```
GET    /v1/users           — list users
POST   /v1/users           — create user
GET    /v1/users/:id       — get user
PATCH  /v1/users/:id       — partial update
DELETE /v1/users/:id       — delete
GET    /v1/users/:id/posts — nested resource
```

**Pagination:**
- Cursor-based for large / real-time datasets
- Offset (`page` + `limit`) for small, stable datasets only
- Always return `total` count in `meta`
- Default limit: 20, max limit: 100

**Anti-patterns:**
- Verbs in URLs: `/getUser`, `/createPost` — use HTTP methods
- Inconsistent response shapes between endpoints
- No versioning: `/users` — always `/v1/users`
- Exposing database IDs directly — use UUIDs or public-facing slugs

---

## 7. TypeScript

**Rule: strict types everywhere. Zod generates types. No `any`.**

**Required:**
```typescript
// Infer from Zod — never define separately
const createUserSchema = z.object({ email: z.string().email() });
type CreateUserInput = z.infer<typeof createUserSchema>; // ✅

// Typed repository returns — never raw Prisma types to callers
interface UserRepository {
  findById(id: string): Promise<UserDTO | null>;
  create(data: CreateUserInput): Promise<UserDTO>;
}

// unknown + parse instead of any
function handleWebhook(payload: unknown): WebhookEvent {
  return webhookEventSchema.parse(payload); // throws on invalid
}
```

**Anti-patterns:**
- `any` — use `unknown` + Zod or type guards
- Returning raw Prisma models from repositories — define DTOs
- Casting with `as SomeType` without validation
- Implicit `any` in catch blocks: `catch (e)` → use `catch (e: unknown)`

---

## 8. File Structure

```
src/
  routes/
    users.router.ts         ← one file per domain
    billing.router.ts
  services/
    user.service.ts         ← business logic, orchestrates repositories
    billing.service.ts
  repositories/
    user.repository.ts      ← Prisma queries
    product.repository.ts   ← Mongoose queries
    cache.repository.ts     ← Redis operations
  schemas/
    user.schema.ts          ← Zod schemas (shared across routes + services)
    billing.schema.ts
  models/
    product.model.ts        ← Mongoose models
  middleware/
    auth.middleware.ts
    error.middleware.ts
    rate-limit.middleware.ts
  lib/
    prisma.ts               ← Prisma client singleton
    mongoose.ts             ← Mongoose connection
    redis.ts                ← Redis client singleton
    errors.ts               ← AppError classes
    logger.ts               ← structured logger
```

**Layer rules (never skip):**
```
Route handler → Service → Repository → Database
     ↑               ↑           ↑
  Validation    Business      Data access
   (Zod)         logic         only here
```

- Routes call services — never repositories directly
- Services call repositories — never Prisma/Mongoose directly
- Repositories return DTOs — never raw DB objects to callers
- Schemas (`src/schemas/`) shared between routes and services — single source of truth

---

## Behavior Rules

- **Answer from these practices first** — when a dev asks about patterns, check here before responding
- **Flag deviations** — if asked to implement something that contradicts these practices, flag it: "This goes against be-best-practices — here's the correct pattern"
- **Repository layer always** — whenever a dev accesses the DB directly in a route or service, flag it
- **Zod schemas before types** — whenever a type is needed, ask if there's a Zod schema it should be inferred from
- **Error classes over raw throws** — always suggest the appropriate AppError subclass
- **Cache invalidation reminder** — whenever a mutation is written, remind about cache invalidation if Redis is in use
