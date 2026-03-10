# 寻根家谱管理系统 - AI Coding Guidelines

## Project Overview
Full-stack family tree/genealogy management system with FastAPI backend and Vue 3 frontend.

**Tech Stack:**
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), SQLite, Pydantic
- **Frontend:** Vue 3, TypeScript 5.3, Vite, Pinia, Element Plus, D3.js

---

## Build/Lint/Development Commands

### Frontend (./frontend/)
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
4. Export in `app/routers/__init__.py`
5. Add frontend API in `@/api/`
6. Add TypeScript types in `@/types/index.ts`

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

frontend/
├── src/
│   ├── api/         # API layer (axios wrappers)
│   ├── views/       # Page components
│   ├── components/  # Reusable UI components
│   ├── stores/      # Pinia state management
│   ├── types/       # TypeScript interfaces
│   └── router/      # Vue Router configuration
└── public/          # Static assets
```
