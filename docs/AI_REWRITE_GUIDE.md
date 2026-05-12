# AI 改写功能使用说明

## 当前入口

- 管理后台页面：`/admin/ai-generator`
- 后端接口：
  - `POST /api/v1/articles/ai-rewrite`
  - `GET /api/v1/articles/ai-progress`
  - `POST /api/v1/articles/ai-tasks/clear`

## 依赖配置

在 `backend/.env` 中至少补这几个变量：

```env
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_MODEL=MiniMax-M2.7
MINIMAX_API_HOST=https://api.minimaxi.com/v1/chat/completions
```

如果当前环境还没装抓取依赖，需要在 `backend/` 执行：

```bash
venv/bin/pip install -r requirements.txt
```

## 使用方式

1. 打开后台 `AI 改写`
2. 输入微信公众号文章链接
3. 选择改写策略和模板
4. 选择保存草稿或直接发布
5. 提交后在页面右侧和下方查看进度与历史任务

## 当前实现说明

- 任务状态目前保存在后端内存里，后端重启后历史任务会清空
- AI 生成后的文章会保存到当前 Flask 使用的 `backend/instance/blog.db`
- 如果选择“保存草稿”，完成后可直接跳转到文章编辑页继续修改
   - 人工审核是必要的
   - 避免敏感话题

3. **版权合规**
   - 改写不等于抄袭
   - 保留核心思想，重写表达
   - 必要时标注参考来源

---

## 📞 技术支持

如有问题，请：
1. 查看本文档
2. 检查控制台错误信息
3. 查看任务错误详情

---

## 📝 更新日志

### v1.0.0 (2026-05-10)
- ✨ 初始版本发布
- ✅ 支持微信文章抓取
- ✅ 支持 MiniMax AI 改写
- ✅ 支持多种改写策略
- ✅ 支持任务进度监控
