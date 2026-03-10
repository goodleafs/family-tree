# 寻根家谱管理系统

基于 FastAPI + Vue3 的多家族寻根家谱管理系统

## 功能特性

- ✅ **多家族管理**：创建和管理多个家族，包含家族史、家训、字辈等信息
- ✅ **成员管理**：添加家族成员，记录详细信息（生卒日期、职业、教育等）
- ✅ **亲属关系**：建立父子、配偶等亲属关系
- ✅ **家谱树可视化**：使用 D3.js 展示家谱树，支持交互操作
- ✅ **灵堂祭拜**：可以给已经逝世的族人设置灵堂，并进行祭拜活动
- ✅ **用户认证**：JWT 认证系统，支持注册登录
- ✅ **权限管理**：管理员/编辑者/成员三级权限
- 📦 **PDF 导出**：生成专业家谱图（开发中）
- 📦 **Excel 导入**：批量导入成员数据（开发中）
- 📦 **打印预览**：打印效果实时预览（开发中）
- ✅ **响应式设计**：支持移动端访问

## 技术栈

### 后端
- **FastAPI**: 现代、快速的 Python Web 框架
- **SQLAlchemy 2.0**: ORM 数据库操作
- **SQLite + aiosqlite**: 异步数据库
- **JWT**: 用户认证
- **ReportLab**: PDF 生成
- **OpenPyXL**: Excel 处理

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全
- **Vite**: 前端构建工具
- **Element Plus**: UI 组件库
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **D3.js**: 数据可视化

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/goodleafs/family-tree.git
cd family-tree
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在 http://localhost:8000

API 文档访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 http://localhost:5173

### 4. 访问应用

打开浏览器访问 http://localhost:5173

默认登录：
- 超级管理员用户名：yunxing   密码：admin123

## 项目结构

```
genealogy-system/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py      # 应用入口
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── routers/     # API 路由
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── uploads/         # 上传文件
│   └── requirements.txt # Python 依赖
│
├── frontend/             # Vue3 前端
│   ├── src/
│   │   ├── api/         # API 请求
│   │   ├── views/       # 页面视图
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # 状态管理
│   │   └── types/       # TypeScript 类型
│   └── package.json     # Node.js 依赖
│
├── database/             # SQLite 数据库文件
└── design.md             # 设计文档
```

## API 接口

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户
- `PUT /api/v1/auth/me` - 更新用户信息

### 家族管理
- `GET /api/v1/families` - 获取家族列表
- `POST /api/v1/families` - 创建家族
- `GET /api/v1/families/{id}` - 获取家族详情
- `PUT /api/v1/families/{id}` - 更新家族
- `DELETE /api/v1/families/{id}` - 删除家族

### 成员管理
- `GET /api/v1/persons/family/{family_id}` - 获取家族成员
- `POST /api/v1/persons` - 创建成员
- `GET /api/v1/persons/{id}` - 获取成员详情
- `PUT /api/v1/persons/{id}` - 更新成员
- `DELETE /api/v1/persons/{id}` - 删除成员
- `GET /api/v1/persons/{id}/tree` - 获取家谱树

## 开发计划

- [x] 基础架构搭建
- [x] 用户认证系统
- [x] 家族管理功能
- [x] 成员管理功能
- [x] 家谱树 API
- [ ] PDF 导出功能
- [ ] Excel 导入功能
- [ ] 打印预览功能
- [ ] D3.js 家谱树可视化
- [ ] 移动端适配优化

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
