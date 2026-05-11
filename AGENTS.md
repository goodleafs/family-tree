# 寻根族谱管理系统 - AI Coding Guidelines

## Project Overview
Full-stack family tree/genealogy management system with FastAPI backend and Vue 3 frontend.

**Tech Stack:**
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), SQLite, Pydantic
- **Frontend (v1):** Vue 3, TypeScript 5.3, Vite, Pinia, Element Plus, D3.js
- **Frontend (v2 - 主推):** Vue 3, TypeScript 5.3, Vite, Pinia, D3.js, 自定义组件库（中式典雅风格）
- **前端版本说明**: `frontend/` 为旧版（Element Plus），`frontend-v2/` 为新版（主推，后续以 v2 为主）

---

## Build/Lint/Development Commands

### Frontend (./frontend/ - 旧版 Element Plus)
```bash
# Development server
npm run dev

# Production build
npm run build

# TypeScript type checking
npm run typecheck

# Lint (ESLint - config uses defaults)
npm run lint

# Format (Prettier - config uses defaults)
npm run format

# Preview production build
npm run preview
```

### Frontend (./frontend-v2/ - 新版主推)
```bash
# Development server (port 5173)
npm run dev

# Production build
npm run build

# TypeScript type checking
npm run typecheck

# Preview production build
npm run preview
```

### Backend (./backend/)
```bash
# Run development server (from backend/ directory)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python app/main.py
```

### Full Stack (separate terminals)
```bash
# Terminal 1 - Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Note:** No test framework currently configured. When adding tests:
- Python: Add pytest + pytest-asyncio to requirements.txt
- Frontend: Add Vitest for Vue component testing

---

## Code Style Guidelines

### Python (Backend)

#### Imports
```python
# Order: stdlib → third-party → local
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import PersonCreate, PersonResponse
from app.services import PersonService
```

#### Naming Conventions
- **Files:** snake_case (e.g., `person_service.py`, `file_upload.py`)
- **Classes:** PascalCase (e.g., `PersonService`, `PersonCreate`)
- **Functions/Variables:** snake_case (e.g., `get_person_by_id`, `verify_password`)
- **Constants:** UPPER_CASE (e.g., `ACCESS_TOKEN_EXPIRE_MINUTES`)

#### Architecture Pattern (Strict)
**Layered Architecture:** Routers → Services → Models

```python
# Router (app/routers/person.py)
@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: AsyncSession = Depends(get_db)):
    person = await PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    return person

# Service (app/services/person_service.py)
class PersonService:
    @staticmethod
    async def get_person_by_id(db: AsyncSession, person_id: int) -> Optional[Person]:
        result = await db.execute(select(Person).where(Person.id == person_id))
        return result.scalar_one_or_none()
```

#### Error Handling
```python
# Use FastAPI HTTPException for HTTP errors
if not family:
    raise HTTPException(status_code=404, detail="家族不存在")

# Check permissions before operations
role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
if not role:
    raise HTTPException(status_code=403, detail="您没有权限访问此家族")
```

#### Type Hints
- Always use type hints for function parameters and return types
- Use Pydantic models for request/response validation
- Use `Optional[Type]` for nullable values

---

### TypeScript/Vue (Frontend)

#### Imports
```typescript
// Order: Vue → third-party → @/ aliases
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

import { personApi } from '@/api/person'
import type { Person, FamilyTree } from '@/types'
import { useUserStore } from '@/stores/user'
```

#### Naming Conventions
- **Components:** PascalCase (e.g., `PersonDetail.vue`, `FamilyTree.vue`)
- **Types/Interfaces:** PascalCase (e.g., `Person`, `FamilyTree`, `ListResponse`)
- **Variables/Functions:** camelCase (e.g., `selectedPerson`, `fetchData`)
- **API Objects:** camelCase + Api suffix (e.g., `personApi`, `familyApi`)

#### Vue 3 Composition API Pattern
```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { personApi } from '@/api/person'
import type { Person } from '@/types'

// Reactive refs with explicit types
const person = ref<Person | null>(null)
const loading = ref<boolean>(false)

// Methods
const fetchPerson = async (id: number) => {
  loading.value = true
  try {
    person.value = await personApi.getPerson(id)
  } catch (error) {
    ElMessage.error('获取成员信息失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const route = useRoute()
  fetchPerson(Number(route.params.id))
})
</script>
```

#### API Layer Pattern
```typescript
// @/api/person.ts
import request from './request'
import type { Person, ListResponse } from '@/types'

export const personApi = {
  getPerson: (id: number): Promise<Person> => {
    return request.get(`/persons/${id}`)
  },
  
  createPerson: (data: Partial<Person>): Promise<Person> => {
    return request.post('/persons', data)
  }
}
```

#### Error Handling
```typescript
// Use Element Plus ElMessage for user feedback
try {
  await personApi.deletePerson(id)
  ElMessage.success('删除成功')
} catch (error) {
  ElMessage.error('删除失败')
}
```

---

## Database & Models

### SQLAlchemy 2.0 (Async)
```python
# Always use async session
from sqlalchemy.ext.asyncio import AsyncSession

# Define relationships with back_populates
class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    family: Mapped["Family"] = relationship("Family", back_populates="persons")
```

---

## Security Considerations

- JWT authentication required for protected routes
- Check family permissions (public/private) before returning data
- Validate file uploads (type, size limit 10MB)
- Never commit `.env` files or hardcoded secrets

---

## Common Tasks

### Adding a New API Endpoint
1. Define Pydantic schemas in `app/schemas/`
2. Add service method in `app/services/`
3. Create router endpoint in `app/routers/`
4. Export in `app/routers/__init__.py` and register in `app/main.py`
5. Add frontend API in `@/api/`（如 `frontend/src/api/` 和 `frontend-v2/src/api/`）
6. Add TypeScript types in `@/types/index.ts`（两个前端目录都需要更新）

### Adding a New Backend Model (遵循已有模式)
1. 在 `app/models/` 中创建新模型文件（参考 `album.py` 或 `document.py` 的写法）
2. 在 `app/models/__init__.py` 中导出
3. 如有需要在 `app/models/user.py`、`app/models/family.py` 等关联模型中添加 relationship

### Adding a New Frontend View (frontend-v2)
1. 在 `frontend-v2/src/views/` 下创建视图目录和文件
2. 使用自定义组件（GCard、GButton、GInput）而非 Element Plus
3. 使用 CSS 变量（`--cinnabar`、`--bg-primary` 等）保持一致风格
4. 在 `frontend-v2/src/router/index.ts` 中添加路由（带 `meta.title`）

### Database Migrations
Currently using SQLite auto-create. For production, add Alembic:
```bash
pip install alembic
alembic init alembic
```

---

## File Organization

```
backend/
├── app/
│   ├── routers/     # API route handlers (HTTP layer)
│   ├── services/    # Business logic (database operations)
│   ├── models/      # SQLAlchemy ORM models
│   ├── schemas/     # Pydantic validation models
│   ├── utils/       # Helper functions (auth, file upload)
│   ├── config.py    # Settings (pydantic-settings)
│   └── database.py  # Async DB session setup
└── uploads/         # File uploads (ignored in git)

frontend/ (旧版 - Element Plus)
├── src/
│   ├── api/         # API layer (axios wrappers)
│   ├── views/       # Page components
│   ├── components/  # Reusable UI components
│   ├── stores/      # Pinia state management
│   ├── types/       # TypeScript interfaces
│   └── router/      # Vue Router configuration
└── public/          # Static assets

frontend-v2/ (新版 - 主推)
├── src/
│   ├── api/         # API layer (axios wrappers)
│   ├── views/       # Page components
│   ├── components/  # Reusable UI components (common/layout)
│   ├── stores/      # Pinia state management
│   ├── types/       # TypeScript interfaces
│   └── router/      # Vue Router configuration
└── public/          # Static assets
```
