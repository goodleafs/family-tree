# 更新日志

所有显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.0.0] - 2026-05-11

### 概述

全面升级至 v2.0.0，引入全新中式典雅风格前端，新增四大核心功能模块，全面优化移动端体验。

### 新增

- **家族相册功能**
  - 新增 `Album` 和 `Photo` 数据库模型，支持相册集管理和照片上传
  - 相册列表视图 + 时间轴视图（按年份分组展示）
  - 支持照片标题、拍摄日期、缩略图生成
  - 照片标题默认"未命名"，上传后支持编辑修改
  - API: `/api/v1/albums/*` 共 10 个端点
  - 前端：`frontend/src/views/album/` + `frontend-v2/src/views/album/`

- **文献库功能**
  - 新增 `Document` 数据库模型，支持 PDF/图片/Word 等文献上传
  - 文献分类（老谱扫描、契约文书、著作文献、其他）
  - 分类统计概览、关键词搜索、内联预览（图片/PDF）
  - API: `/api/v1/documents/*` 共 7 个端点
  - 前端：`frontend/src/views/document/` + `frontend-v2/src/views/document/`

- **人物传记功能**
  - 新增 `PersonBiography` 数据库模型，支持 HTML 富文本传记
  - 传记列表 + 详情页 + 编辑模式，支持浏览量统计
  - API: `/api/v1/biographies/*` 共 7 个端点
  - 前端：`frontend/src/views/biography/` + `frontend-v2/src/views/biography/`

- **功德榜功能**
  - 新增 `MeritDonor` 数据库模型，记录宗亲修谱捐款
  - 金额排行展示，前三名奖牌标识
  - 捐款人次和总额统计
  - API: `/api/v1/merit/*` 共 5 个端点
  - 前端：`frontend-v2/src/views/merit/`

- **新版前端 (frontend-v2)**
  - 全新中式传统典雅风格 UI
  - 自定义组件库（GCard、GButton、GInput），替代 Element Plus
  - 内联 SVG 图标体系，CSS 变量驱动主题
  - 逐步取代旧版前端成为主前端

### 优化

- **交互体验**
  - 家族详情页各功能 tab 直接展示核心内容，无需二次跳转
  - 族谱树 tab 自动以第一代成员为根节点加载，无需手动选择
  - 照片上传后支持编辑标题和拍摄日期

- **移动端适配**
  - 全局响应式断点（768px/480px）
  - 表格卡片化布局，横向可滚动
  - 触摸目标最小 36px 优化
  - 所有对话框移动端全宽适配

### 修改

- **后端配置扩展**
  - `config.py`：新增 `ALLOWED_DOCUMENT_TYPES`、`MAX_DOCUMENT_SIZE`、上传子目录配置
  - `file_upload.py`：新增 `validate_document()`，支持文档类型验证
- **后端模型扩展**
  - `user.py`：新增 7 个关系（albums/photos/documents/biographies/merit）
  - `family.py`：新增 5 个关系
  - `person.py`：新增 biography_entry 关系
- **文档更新**
  - 根目录 README/AGENTS/design 全部同步更新
  - 新建 `RELEASE-v2.0.0.md` 版本发布说明

### 技术变更

- **后端新增模型**：Album、Photo、Document、PersonBiography、MeritDonor
- **后端新增 API 端点**：相册 10 + 文献 7 + 传记 7 + 功德榜 5 = 共 29 个新端点
- **文件上传扩展**：新增文档类型验证，支持 PDF/Word 上传
- **前端双版本并行**：v1（Element Plus）+ v2（自定义组件库，主推）

## [1.0.0] - 2026-03-11

### 新增

- **农历日期显示功能**
  - 安装 `lunar-javascript` 库用于农历转换
  - 在成员详情页显示出生日期和逝世纪念的农历日期
  - 支持干支纪年格式，如"甲辰年正月初一"
  - 在灵堂详情页牌位上显示农历日期
  - 创建 `frontend/src/utils/lunar.ts` 工具函数模块

- **PDF导出功能**
  - 安装 `html2pdf.js` 库用于PDF生成
  - 在成员详情页添加"导出PDF"按钮
  - 支持导出A4格式PDF，包含完整的成员信息
  - PDF内容包括：基本信息、出身详情、教育职业、生平事迹、家族成员、亲属关系
  - 文件命名格式：`{成员姓名}_家族成员信息.pdf`

- **成员删除功能**
  - 在家族详情页成员列表中添加删除按钮
  - 实现删除确认对话框，防止误删
  - 删除成功后自动刷新成员列表

### 修改

- **文本长度限制调整**
  - 家族史：从1000字调整为2000字
  - 家训：从200字调整为2000字

### 技术变更

- **前端依赖**
  - 新增 `lunar-javascript@^1.2.4` - 农历日期转换
  - 新增 `html2pdf.js@^0.10.1` - PDF导出功能

## [0.9.0] - 2026-03-10

### 新增

- 族谱管理系统初始版本
- 用户注册登录功能
- 家族创建和管理功能
- 成员信息管理功能
- 族谱树可视化展示
- 灵堂祭拜功能
- 成员关系管理

---

**提交哈希**: `cab532b`
**提交者**: opencode
