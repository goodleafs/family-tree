# 寻根族谱管理系统 - 设计文档

## 项目概述

一个基于 FastAPI + SQLite + Vue3 的多家族寻根族谱管理系统，支持族谱可视化、PDF导出、打印预览和Excel批量导入等功能。

## 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **数据库**: SQLite + SQLAlchemy 2.0.23
- **ORM**: SQLAlchemy 2.0 async (selectinload)
- **认证**: JWT + bcrypt
- **PDF生成**: ReportLab 4.0.7
- **Excel处理**: OpenPyXL 3.1.2
- **图片处理**: Pillow 10.1.0

### 前端 (v1 - Element Plus)
- **框架**: Vue 3.3.8 + TypeScript
- **构建工具**: Vite 5.0.0
- **UI组件库**: Element Plus 2.4.4
- **状态管理**: Pinia 2.1.7
- **路由**: Vue Router 4.2.5
- **可视化**: D3.js 7.8.5
- **HTTP客户端**: Axios 1.6.2
- **Excel解析**: xlsx 0.18.5

### 前端 (v2 - 主推，中式传统典雅风格)
- **框架**: Vue 3 + TypeScript 5.3
- **构建工具**: Vite 5.x
- **UI**: 自定义组件库（GCard、GButton、GInput）
- **样式**: CSS 变量体系（--cinnabar朱砂红、--indigo靛蓝、--bamboo竹绿等）
- **状态管理**: Pinia 2.1.7
- **路由**: Vue Router 4.x
- **可视化**: D3.js 7.x
- **HTTP客户端**: Axios 1.6.x
- **工具库**: @vueuse/core 10.x, lunar-javascript 1.x

## 项目目录结构

```
family-tree/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── main.py              # FastAPI 入口（注册所有路由）
│   │   ├── config.py            # 配置（pydantic-settings）
│   │   ├── database.py          # 异步数据库连接
│   │   ├── jwt.py               # JWT 配置
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # 用户
│   │   │   ├── family.py        # 家族 + 家族成员角色
│   │   │   ├── person.py        # 人员 + 亲属关系
│   │   │   ├── memorial.py      # 灵堂 + 祭拜记录
│   │   │   ├── album.py         # 相册 + 照片
│   │   │   ├── document.py      # 文献
│   │   │   └── biography.py     # 人物传记
│   │   ├── schemas/             # Pydantic 校验
│   │   │   ├── __init__.py
│   │   │   ├── user.py / family.py / person.py
│   │   │   ├── memorial.py / album.py / document.py / biography.py
│   │   ├── routers/             # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py / family.py / person.py
│   │   │   ├── memorial.py / admin.py
│   │   │   ├── album.py / document.py / biography.py
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py / family_service.py / person_service.py
│   │   │   ├── memorial_service.py
│   │   │   ├── album_service.py / document_service.py / biography_service.py
│   │   └── utils/               # 工具函数
│   │       ├── auth.py          # JWT + bcrypt
│   │       └── file_upload.py   # 文件上传（含文档验证）
│   ├── uploads/                 # 上传文件（photos/albums/documents/avatars）
│   └── requirements.txt
│
├── frontend/                     # Vue3 前端（旧版 - Element Plus）
│   ├── src/
│   │   ├── main.ts / App.vue
│   │   ├── router/index.ts
│   │   ├── stores/user.ts
│   │   ├── api/                 # request.ts + auth/family/person/memorial/album/document/biography
│   │   ├── views/               # auth/dashboard/family/person/memorial/album/document/biography
│   │   ├── types/index.ts
│   │   └── utils/lunar.ts
│   ├── index.html / package.json / vite.config.ts / tsconfig.json
│
├── frontend-v2/                  # Vue3 前端（新版主推 - 中式典雅风格）
│   ├── src/
│   │   ├── main.ts / App.vue
│   │   ├── router/index.ts
│   │   ├── stores/user.ts
│   │   ├── api/                 # request.ts + auth/family/person/memorial/album/document/biography/admin
│   │   ├── views/               # auth/dashboard/family/person/memorial/album/document/biography/user/admin
│   │   ├── components/          # common(GCard/GButton/GInput) + layout(AppLayout/AppHeader/AppSidebar)
│   │   ├── types/index.ts
│   │   └── utils/lunar.ts
│   ├── index.html / package.json / vite.config.ts / tsconfig.json
│
├── database/                     # SQLite 数据库
│   └── genealogy.db
│
├── README.md                     # 项目说明
├── AGENTS.md                     # AI 编码规范
├── CHANGELOG.md                  # 变更日志
└── design.md                     # 设计文档（本文档）
```

## 数据库模型设计

### 用户表 (User)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 家族表 (Family)
```sql
CREATE TABLE families (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,              -- 家族名称
    surname VARCHAR(50),                      -- 家族姓氏
    description TEXT,                         -- 家族简介
    history TEXT,                             -- 家族史
    family_motto TEXT,                        -- 家训/家规
    generation_names TEXT,                    -- 字辈排列 (JSON)
    creator_id INTEGER NOT NULL,              -- 创建人
    is_public BOOLEAN DEFAULT FALSE,          -- 是否公开
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);
```

### 家族成员角色表 (FamilyMember)
```sql
CREATE TABLE family_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,                 -- 关联用户（可选）
    role VARCHAR(20) DEFAULT 'member',        -- 角色：admin, editor, member
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(family_id, user_id)
);
```

### 家族成员表 (Person)
```sql
CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),                       -- male/female
    birth_date DATE,
    death_date DATE,
    birthplace VARCHAR(100),                  -- 出生地
    residence VARCHAR(100),                   -- 现居地
    occupation VARCHAR(100),                  -- 职业
    education VARCHAR(100),                   -- 教育背景
    biography TEXT,                           -- 生平介绍
    achievements TEXT,                        -- 主要成就
    photo_url VARCHAR(255),
    branch_name VARCHAR(50),                  -- 支系/房系
    generation_number INTEGER,                -- 世代
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### 亲属关系表 (Relationship)
```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,               -- 当前成员
    relative_id INTEGER NOT NULL,             -- 关联成员
    relation_type VARCHAR(20) NOT NULL,       -- father, mother, spouse, child
    is_primary BOOLEAN DEFAULT TRUE,          -- 是否主要配偶
    marriage_date DATE,                       -- 结婚日期
    divorce_date DATE,                        -- 离婚日期（如适用）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(id),
    FOREIGN KEY (relative_id) REFERENCES persons(id),
    UNIQUE(person_id, relative_id, relation_type)
);
```

### 家族事件表 (FamilyEvent) - 可选
```sql
CREATE TABLE family_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    event_type VARCHAR(50),                   -- wedding, birthday, memorial
    title VARCHAR(100),
    description TEXT,
    event_date DATE,
    location VARCHAR(100),
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id)
);
```

### 相册表 (Album)
```sql
CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,               -- 相册名称
    description TEXT,                          -- 相册描述
    cover_url VARCHAR(255),                   -- 封面照片URL
    sort_order INTEGER DEFAULT 0,             -- 排序
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### 照片表 (Photo)
```sql
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER,                          -- 所属相册（NULL表示未归类）
    family_id INTEGER NOT NULL,
    title VARCHAR(200),                        -- 照片标题
    description TEXT,
    url VARCHAR(255) NOT NULL,                 -- 文件路径
    thumbnail_url VARCHAR(255),                -- 缩略图路径
    taken_date DATE,                           -- 拍摄日期
    taken_year INTEGER,                        -- 拍摄年份（用于时间轴）
    taken_month INTEGER,
    file_size INTEGER,
    uploader_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (uploader_id) REFERENCES users(id)
);
```

### 文献表 (Document)
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,              -- 文献标题
    description TEXT,
    file_type VARCHAR(50) NOT NULL,           -- pdf, image, doc, other
    file_url VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_ext VARCHAR(20),                     -- 文件扩展名
    author VARCHAR(100),                      -- 文献作者
    document_date VARCHAR(50),                -- 文献日期（原文）
    tags VARCHAR(500),                        -- 标签（逗号分隔）
    category VARCHAR(50),                     -- 分类: genealogy/contract/writing/other
    uploader_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (uploader_id) REFERENCES users(id)
);
```

### 人物传记表 (PersonBiography)
```sql
CREATE TABLE person_biographies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL UNIQUE,        -- 关联人员
    family_id INTEGER NOT NULL,
    title VARCHAR(200),                       -- 传记标题（如"XX公传"）
    subtitle VARCHAR(300),                    -- 副标题
    summary TEXT,                             -- 摘要/导语
    content TEXT NOT NULL,                    -- 传记正文（支持HTML）
    achievements TEXT,                        -- 主要成就
    portrait_url VARCHAR(255),               -- 传记专用肖像
    is_published BOOLEAN DEFAULT TRUE,
    views_count INTEGER DEFAULT 0,           -- 浏览次数
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(id),
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

## API 接口设计

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/me` - 获取当前用户信息
- `PUT /api/v1/auth/me` - 更新用户信息

### 家族管理
- `GET /api/v1/families` - 获取家族列表（支持搜索、分页）
- `POST /api/v1/families` - 创建家族
- `GET /api/v1/families/{id}` - 获取家族详情
- `PUT /api/v1/families/{id}` - 更新家族信息
- `DELETE /api/v1/families/{id}` - 删除家族
- `GET /api/v1/families/{id}/members` - 获取家族成员列表
- `POST /api/v1/families/{id}/members` - 添加家族成员

### 成员管理
- `GET /api/v1/persons/{id}` - 获取成员详情
- `POST /api/v1/persons` - 创建成员
- `PUT /api/v1/persons/{id}` - 更新成员信息
- `DELETE /api/v1/persons/{id}` - 删除成员
- `POST /api/v1/persons/{id}/photo` - 上传成员照片

### 关系管理
- `GET /api/v1/persons/{id}/tree` - 获取成员族谱树
- `POST /api/v1/relationships` - 创建亲属关系
- `DELETE /api/v1/relationships/{id}` - 删除亲属关系

### 家族相册
- `GET /api/v1/albums/family/{family_id}` - 获取家族相册列表
- `POST /api/v1/albums` - 创建相册
- `GET /api/v1/albums/{album_id}` - 获取相册详情（含照片）
- `PUT /api/v1/albums/{album_id}` - 更新相册信息
- `DELETE /api/v1/albums/{album_id}` - 删除相册
- `GET /api/v1/albums/{album_id}/photos` - 获取相册照片列表
- `POST /api/v1/albums/{album_id}/photos` - 上传照片到相册
- `PUT /api/v1/albums/photos/{photo_id}` - 更新照片信息
- `DELETE /api/v1/albums/photos/{photo_id}` - 删除照片
- `GET /api/v1/albums/family/{family_id}/timeline` - 获取家族照片时间轴

### 文献管理
- `GET /api/v1/documents/family/{family_id}` - 获取家族文献列表（支持分类+搜索）
- `GET /api/v1/documents/family/{family_id}/overview` - 获取文献库概览（分类统计）
- `POST /api/v1/documents` - 上传文献
- `GET /api/v1/documents/{document_id}` - 获取文献详情
- `PUT /api/v1/documents/{document_id}` - 更新文献信息
- `DELETE /api/v1/documents/{document_id}` - 删除文献

### 人物传记
- `GET /api/v1/biographies/family/{family_id}` - 获取家族传记列表
- `POST /api/v1/biographies` - 创建传记
- `GET /api/v1/biographies/{biography_id}` - 获取传记详情（自动增加浏览数）
- `PUT /api/v1/biographies/{biography_id}` - 更新传记
- `DELETE /api/v1/biographies/{biography_id}` - 删除传记
- `GET /api/v1/biographies/eligible-persons/{family_id}` - 获取可创建传记的人员列表
- `GET /api/v1/biographies/by-person/{person_id}` - 按人员ID获取传记

### 文件上传
- `POST /api/v1/upload/photo` - 上传照片（旧接口，建议使用相册上传）

### 导出功能
- `GET /api/v1/families/{id}/export/pdf` - 导出完整家族PDF
- `GET /api/v1/persons/{id}/export/pdf` - 导出个人支系PDF
- `GET /api/v1/families/{id}/export/excel` - 导出Excel数据

### 导入功能
- `POST /api/v1/families/{id}/import/excel` - Excel批量导入成员
- `GET /api/v1/import/template` - 下载导入模板
- `POST /api/v1/import/validate` - 验证导入数据

### 打印预览
- `POST /api/v1/families/{id}/print/preview` - 生成打印预览HTML

## 核心功能模块

### 族谱树可视化方案

**技术选型**: D3.js + 自定义力导向图

**功能特性**:
- **树形布局**: 上下/左右/径向三种布局模式
- **交互功能**:
  - 点击节点：查看/编辑成员详情
  - 双击节点：展开/折叠子树
  - 拖拽：移动节点位置
  - 滚轮/双指：缩放画布
  - 右键菜单：添加亲属、删除节点
- **连接线**: 不同关系类型用不同颜色/样式
  - 实线：父子关系
  - 虚线：配偶关系
  - 双实线：兄弟姐妹

### PDF导出方案

**技术选型**: ReportLab

**导出模板**:
```
┌─────────────────────────────────────┐
│  [家族名称] 族谱图                    │
│  家训：[家训内容]                     │
│  导出日期：2024-01-01                │
├─────────────────────────────────────┤
│                                     │
│      [族谱树可视化图表]               │
│                                     │
├─────────────────────────────────────┤
│  [成员详细信息列表]                   │
│  - 第1代：始祖姓名、生卒日期...       │
│  - 第2代：...                        │
├─────────────────────────────────────┤
│  制谱人：[用户名]                     │
│  家族管理系统生成                     │
└─────────────────────────────────────┘
```

**导出选项**:
- 多种布局：树形图、世系表、列表视图
- 纸张尺寸：A4、A3、A2 横向/纵向
- 样式定制：传统中式/现代简约风格
- 内容选择：照片、生平、配偶信息
- 水印支持：家族印章/水印
- 分页优化：自动分页处理

### 打印预览功能

**实现方案**:
- Vue 组件：模拟 A4/A3 纸张尺寸
- CSS 打印媒体查询优化
- 页眉/页脚自动生成
- 分页预览支持

**功能特性**:
- 实时预览：所见即所得的打印效果
- 纸张设置：A4/A3，横向/纵向切换
- 边距调整：自定义页边距
- 页眉/页脚：自动添加家族名称、页码
- 打印优化：自动缩放族谱图适应纸张
- 浏览器打印：直接调用系统打印对话框

### Excel批量导入功能

**技术选型**: OpenPyXL + Pandas

**Excel模板**:

**模板1：成员基本信息表**
| 序号 | 姓名 | 性别 | 出生日期 | 去世日期 | 字辈 | 父亲姓名 | 母亲姓名 | 配偶姓名 | 职业 | 学历 | 居住地 | 生平简介 |

**模板2：关系定义表**
| 成员A姓名 | 关系类型 | 成员B姓名 | 关系说明 |
| 张三      | 父亲     | 张四      |          |
| 张三      | 配偶     | 李氏      | 元配     |

**数据验证规则**:
- 必填字段：姓名、性别
- 日期格式：YYYY-MM-DD
- 关系一致性检查
- 重复姓名标记（同一家族内）
- 世代顺序逻辑检查
- 配偶关系双向验证

### 移动端适配

**响应式设计**:
- 桌面端：侧边导航 + 主要内容区
- 平板端：可折叠侧边栏
- 移动端：底部 Tab 导航 + 抽屉菜单

**触摸优化**:
- 双指缩放族谱树
- 长按菜单操作
- 滑动切换页面

## 依赖列表

### 后端依赖 (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pillow==10.1.0
reportlab==4.0.7
openpyxl==3.1.2
pandas==2.1.3
```

### 前端依赖 (package.json)
```json
{
  "dependencies": {
    "vue": "^3.3.8",
    "element-plus": "^2.4.4",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.2",
    "d3": "^7.8.5",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "typescript": "^5.3.2",
    "vite": "^5.0.0"
  }
}
```

## 功能清单总结

✅ 多家族管理 - 创建多个独立家族，含家族史、家训、字辈  
✅ 用户认证 - JWT + bcrypt 安全认证系统  
✅ 权限管理 - 管理员/编辑者/成员三级权限  
✅ 族谱可视化 - D3.js 交互式树形图（缩放/拖拽/点击查看）  
✅ 祭拜管理 - 灵堂布置、在线供奉、追思留言  
✅ 家族相册 - 相册集管理、照片上传、时间轴展示  
✅ 文献库 - 文献上传、分类管理、PDF/图片预览  
✅ 人物传记 - 独立传记页面、富文本编辑、浏览量统计  
✅ PDF 导出 - 成员信息导出（html2pdf.js）  
✅ Excel 导入 - 批量导入成员数据  
✅ 响应式设计 - 桌面/平板/移动端适配  
✅ 前端双版本 - v1（Element Plus）+ v2（自定义中式风格）  
✅ 本地文件存储 - 文件系统 + 缩略图生成  

---

**设计完成日期**: 2024年  
**版本**: v1.0.0
