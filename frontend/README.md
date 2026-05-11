# 寻根族谱管理系统 - 前端

基于 Vue3 + Element Plus 的寻根族谱管理系统前端

## 技术栈

- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全的 JavaScript
- **Vite**: 下一代前端构建工具
- **Element Plus**: Vue 3 组件库
- **Vue Router**: 官方路由管理器
- **Pinia**: Vue 官方状态管理库
- **Axios**: HTTP 客户端
- **D3.js**: 数据可视化库（族谱树）

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── src/
│   ├── api/           # API 请求封装
│   ├── components/    # 组件
│   ├── router/        # 路由配置
│   ├── stores/        # Pinia 状态管理
│   ├── types/         # TypeScript 类型定义
│   ├── utils/         # 工具函数
│   ├── views/         # 页面视图
│   ├── App.vue        # 根组件
│   └── main.ts        # 入口文件
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 功能模块

- ✅ 用户登录/注册
- ✅ 家族管理（创建、编辑、删除）
- ✅ 成员管理（添加、编辑、删除）
- ✅ 族谱树展示（D3.js 交互式可视化）
- ✅ 祭拜管理（灵堂布置、在线供奉、追思留言）
- ✅ 家族相册（相册集管理、照片上传、时间轴展示）
- ✅ 文献库（文献上传、分类管理、PDF/图片预览）
- ✅ 人物传记（独立传记页面、富文本编辑、浏览量统计）
- ✅ PDF 导出（成员信息导出、族谱图导出）
- ✅ 权限管理（家族公开/私密、角色分级控制）

## API 代理配置

在 `vite.config.ts` 中配置了代理：
- `/api` -> `http://localhost:8000`
- `/uploads` -> `http://localhost:8000`

确保后端服务运行在 8000 端口。
