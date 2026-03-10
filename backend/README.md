# 寻根家谱管理系统后端

基于 FastAPI + SQLite 的寻根家谱管理系统后端 API

## 技术栈

- **FastAPI**: 现代、快速的 Python Web 框架
- **SQLAlchemy 2.0**: ORM 数据库操作
- **SQLite + aiosqlite**: 异步数据库
- **JWT**: 用户认证
- **Pydantic**: 数据验证

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行服务

```bash
# 开发模式（自动重载）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python app/main.py
```

### 3. API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── config.py         # 配置文件
│   ├── database.py       # 数据库连接
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic模型
│   ├── routers/          # API路由
│   ├── services/         # 业务逻辑
│   └── utils/            # 工具函数
├── uploads/              # 上传文件存储
└── requirements.txt      # 依赖列表
```

## API 接口

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `PUT /api/v1/auth/me` - 更新用户信息

### 家族管理
- `GET /api/v1/families` - 获取家族列表
- `POST /api/v1/families` - 创建家族
- `GET /api/v1/families/{id}` - 获取家族详情
- `PUT /api/v1/families/{id}` - 更新家族信息
- `DELETE /api/v1/families/{id}` - 删除家族

### 成员管理
- `GET /api/v1/persons/family/{family_id}` - 获取家族成员列表
- `POST /api/v1/persons` - 创建成员
- `GET /api/v1/persons/{id}` - 获取成员详情
- `PUT /api/v1/persons/{id}` - 更新成员信息
- `DELETE /api/v1/persons/{id}` - 删除成员
- `GET /api/v1/persons/{id}/tree` - 获取家谱树

## 配置

在 `app/config.py` 中修改配置，或通过环境变量设置：

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./database/genealogy.db
DEBUG=True
```
