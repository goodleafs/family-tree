# 寻根家谱管理系统

> 一个基于 FastAPI + Vue3 + SQLite 的多家族寻根家谱管理系统，支持家谱可视化、祭拜管理、PDF导出、打印预览和Excel批量导入等功能。

## ✨ 功能特性

### 👥 用户管理
- 用户注册、登录、JWT 身份认证
- 个人资料管理（头像、联系方式等）
- 管理员后台管理系统

### 🏛️ 家族管理
- 创建多个家族，支持私密/公开设置
- 家族信息管理（姓氏、堂号、家训、历史等）
- 字辈管理（支持多代字辈设置）
- 家族成员角色分配（管理员、编辑、普通成员）

### 👨‍👩‍👧‍👦 成员管理
- 完整的成员信息记录（姓名、生卒年月、出生地、职业、教育背景等）
- 照片上传与管理（自动缩略图生成）
- 家族关系建立（父子、配偶、子女关系）
- 多配偶关系支持

### 🌳 家谱可视化
- 基于 D3.js 的交互式家谱树展示
- 支持多代展开/收起
- 点击节点查看成员详情
- 响应式布局适配

### 🙏 祭拜管理
- 已故成员祭拜记录管理
- 虚拟祭品供奉（香、烛、花、果等）
- 在线留言悼念与追思
- 祭拜数据统计与展示
- 祭拜权限管理（家族成员专属）

### 📄 导入导出
- **PDF 导出**: 使用 ReportLab 生成精美家谱 PDF
- **Excel 导入**: 批量导入成员信息
- **打印预览**: 优化打印样式，支持 A4 纸张

### 🔐 权限控制
- 家族访问权限（公开/私密）
- 基于角色的操作权限
- API 级别的权限验证

## 🚀 快速开始

### 环境要求

- **后端**: Python 3.12+
- **前端**: Node.js 18+
- **数据库**: SQLite（已包含）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/family-tree.git
cd family-tree
```

#### 2. 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：http://localhost:8000/docs

#### 3. 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用：http://localhost:5173

### 生产部署

```bash
# 前端构建
cd frontend
npm run build

# 后端生产环境（需要配置 .env 文件）
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 💡 使用示例

### 创建家族

1. 登录系统后，点击"创建家族"按钮
2. 填写家族基本信息（名称、姓氏、简介等）
3. 设置字辈（可选，如："文、章、华、国"）
4. 选择公开或私密

### 添加成员

1. 进入家族详情页，点击"添加成员"
2. 填写成员基本信息
3. 上传成员照片
4. 建立家族关系（选择父亲、配偶等）

### 查看家谱树

1. 在家族详情页点击"家谱树"标签
2. 点击节点可展开/收起子代
3. 双击节点查看成员详细信息
4. 使用鼠标滚轮缩放视图

### 导入成员数据

1. 准备 Excel 文件，格式如下：
   ```
   | 姓名 | 性别 | 出生日期 | 父亲姓名 | 配偶姓名 |
   ```
2. 点击"批量导入"按钮
3. 上传 Excel 文件
4. 系统自动解析并建立关系

### 导出家谱 PDF

1. 选择要导出的成员作为根节点
2. 点击"导出 PDF"按钮
3. 选择导出代数（如：3代、5代、全部）
4. 下载生成的 PDF 文件

### 在线祭拜

1. 进入已故成员详情页
2. 点击"祭拜"按钮进入祭拜页面
3. 选择祭品（香、烛、鲜花、水果、酒等）
4. 点击"供奉"完成祭拜仪式
5. 在追思墙留言悼念（可选）
6. 查看家族祭拜统计和祭拜记录

**祭拜权限说明**：
- 只有家族成员可以对已故成员进行祭拜
- 每位成员的祭拜记录会永久保存
- 支持多次祭拜，累计祭拜次数

## ⚙️ 配置说明

### 后端配置 (backend/app/config.py)

```python
# 数据库配置
DATABASE_URL = "sqlite+aiosqlite:///../database/genealogy.db"

# JWT 配置
SECRET_KEY = "your-secret-key"  # 生产环境请修改
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 文件上传配置
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]

# CORS 配置
ALLOWED_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
```

### 环境变量 (.env)

创建 `backend/.env` 文件：

```env
DEBUG=false
SECRET_KEY=your-production-secret-key
DATABASE_URL=sqlite+aiosqlite:///./database/genealogy.db
FRONTEND_URL=https://your-domain.com
```

### 前端配置 (frontend/vite.config.ts)

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## 🤝 贡献指南

我们欢迎所有形式的贡献，无论是新功能、bug 修复还是文档改进。

## 系统截图

![](/mdimage/ScreenShot_2026-03-10_172515_436.png)

![ScreenShot_2026-03-10_172543_603](/mdimage/ScreenShot_2026-03-10_172543_603.png)

![ScreenShot_2026-03-10_172553_603](/mdimage/ScreenShot_2026-03-10_172553_603.png)

![ScreenShot_2026-03-10_172603_428](/mdimage/ScreenShot_2026-03-10_172603_428.png)

![ScreenShot_2026-03-10_172614_627](/mdimage/ScreenShot_2026-03-10_172614_627.png)

![ScreenShot_2026-03-10_172622_315](/mdimage/ScreenShot_2026-03-10_172622_315.png)

### 开发流程

1. **Fork 项目**
   
   ```bash
   git clone https://github.com/goodleafs/family-tree.git
   cd family-tree
   ```
   
2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **Push 到 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**

### 代码规范

- **Python**: 遵循 PEP 8，使用类型注解
- **TypeScript**: 严格模式，显式类型声明
- **Git Commit**: 使用 [Conventional Commits](https://conventionalcommits.org/) 规范
  - `feat`: 新功能
  - `fix`: Bug 修复
  - `docs`: 文档更新
  - `style`: 代码格式（不影响功能）
  - `refactor`: 代码重构
  - `test`: 测试相关
  - `chore`: 构建/工具相关

### 报告 Bug

请使用 GitHub Issues 报告问题，并提供以下信息：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（操作系统、浏览器版本等）
- 截图（如有）

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

```
MIT License

Copyright (c) 2024 寻根家谱管理系统

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 Email: 25261985@qq.com
- 💬 Issues: [GitHub Issues](https://github.com/goodleafs/family-tree/issues)

**Made with ❤️ for family heritage preservation**
