# 寻根家谱管理系统 - 设计文档

## 项目概述

一个基于 FastAPI + SQLite + Vue3 的多家族寻根家谱管理系统，支持家谱可视化、PDF导出、打印预览和Excel批量导入等功能。

## 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **数据库**: SQLite + SQLAlchemy 2.0.23
- **认证**: JWT + bcrypt
- **PDF生成**: ReportLab 4.0.7
- **Excel处理**: OpenPyXL 3.1.2
- **图片处理**: Pillow 10.1.0

### 前端
- **框架**: Vue 3.3.8 + TypeScript
- **构建工具**: Vite 5.0.0
- **UI组件库**: Element Plus 2.4.4
- **状态管理**: Pinia 2.1.7
- **路由**: Vue Router 4.2.5
- **可视化**: D3.js 7.8.5
- **HTTP客户端**: Axios 1.6.2
- **Excel解析**: xlsx 0.18.5

## 项目目录结构

```
genealogy-system/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置文件
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # 用户模型
│   │   │   ├── family.py        # 家族模型
│   │   │   └── person.py        # 成员模型
│   │   ├── schemas/             # Pydantic 数据验证
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── family.py
│   │   │   └── person.py
│   │   ├── routers/             # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # 认证相关
│   │   │   ├── family.py        # 家族管理
│   │   │   └── person.py        # 成员管理
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── family_service.py
│   │   │   └── person_service.py
│   │   └── utils/               # 工具函数
│   │       ├── __init__.py
│   │       ├── auth.py          # JWT 工具
│   │       └── file_upload.py   # 文件上传
│   ├── uploads/                 # 上传文件存储
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                     # Vue3 前端
│   ├── src/
│   │   ├── main.ts              # Vue 入口
│   │   ├── App.vue
│   │   ├── router/              # Vue Router
│   │   │   └── index.ts
│   │   ├── stores/              # Pinia 状态管理
│   │   │   ├── auth.ts
│   │   │   ├── family.ts
│   │   │   └── person.ts
│   │   ├── api/                 # API 请求封装
│   │   │   ├── request.ts       # axios 封装
│   │   │   ├── auth.ts
│   │   │   ├── family.ts
│   │   │   └── person.ts
│   │   ├── components/          # 组件
│   │   │   ├── common/          # 通用组件
│   │   │   ├── family/          # 家族相关
│   │   │   └── person/          # 成员相关
│   │   ├── views/               # 页面
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── family/
│   │   │   └── person/
│   │   ├── utils/               # 工具函数
│   │   ├── types/               # TypeScript 类型
│   │   └── assets/              # 静态资源
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── database/                     # 数据库文件
│   └── genealogy.db
│
└── README.md
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
- `GET /api/v1/persons/{id}/tree` - 获取成员家谱树
- `POST /api/v1/relationships` - 创建亲属关系
- `DELETE /api/v1/relationships/{id}` - 删除亲属关系

### 文件上传
- `POST /api/v1/upload/photo` - 上传照片

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

### 家谱树可视化方案

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
│  [家族名称] 家谱图                    │
│  家训：[家训内容]                     │
│  导出日期：2024-01-01                │
├─────────────────────────────────────┤
│                                     │
│      [家谱树可视化图表]               │
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
- 打印优化：自动缩放家谱图适应纸张
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
- 双指缩放家谱树
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
✅ 家谱可视化 - D3.js 交互式树形图（缩放/拖拽/点击查看）  
✅ PDF 导出 - ReportLab 专业家谱图（多模板/多尺寸/水印）  
✅ 打印预览 - 实时打印效果预览，支持浏览器打印  
✅ Excel 导入 - 批量导入成员数据，含验证和冲突检测  
✅ 响应式设计 - 移动端优先，触摸优化  
✅ 本地图片存储 - 文件系统 + 缩略图生成  

---

**设计完成日期**: 2024年  
**版本**: v1.0.0
