# 微信公众号文章抓取报告

## 公众号信息

- **名称**: 码哥跳动 (原名：码哥字节)
- **合集名称**: AI
- **总文章数**: 32 篇
- **本次抓取**: 10 篇 (最新)

## 抓取到的文章列表

| 序号 | 文章标题 | 链接 |
|------|---------|------|
| 1 | 图文详细教程，不翻墙也能用 Claude Code + cc-switch 接入 DeepSeek V4 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507305&idx=1&sn=290b3fe50443b927a40bf21773114d13&chksm=c27f9f5ff50816493653797ad2e79392bf683b7af17ed6cbd08e7cf6f3e12330a9f4f2ef7c51#rd) |
| 2 | Claude Code v2.1.139 新增 Agent 视图颠覆了工作流，这次设计比功能更值得看 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507287&idx=1&sn=4ff81ba80346630e2918a3e368eb466e&chksm=c27f9f61f50816774b9414b338949f9727e85e9f4d8f66e980ee434e8ff59bc514d5ffed7fd6#rd) |
| 3 | 185000 星的 Superpowers 插件，90% 的人只用了它 10% 的功能 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507267&idx=1&sn=776a7138fc3c9129011f76f3365ab92a&chksm=c27f9f75f5081663b0d980eb9ba0eb52b78d5ce740f6f27dae62f7afed8220e77ff9d685781f#rd) |
| 4 | 总觉得 Claude Code 写完代码有问题？我用了一个开源 Skill 编排了 7 阶段严谨开发工作流，拦下 10 个 Critical Bug | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507231&idx=1&sn=71b5621ff52ff7bea9e4881afeabf88c&chksm=c27f9f29f508163f62168252a3a57d138fbdd14f8b18d71daf72c565224b878020f8c7b86bdc#rd) |
| 5 | Google 开源了一个 14900 Star 项目，让 AI Agent 碰数据库不再是定时炸弹 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507229&idx=1&sn=e02b91f1e3095f903846ca5a5e791395&chksm=c27f9f2bf508163da613e6d971a8465e62bb2ec52275a0f2f2e9e75481f90f7f0adc91c52a72#rd) |
| 6 | 2026 年了，AI 编程还停在「让它写函数」？这个差距正在变大 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507227&idx=1&sn=d8f95d09bc1f018a176e16901dfa8aa3&chksm=c27f9f2df508163b152ad7834b6006564d6d0cc60940e6a9189c78d3e26b358fac5a50e5a820#rd) |
| 7 | 我把 4 年踩坑经验「蒸馏」成 Claude Code Skill 开源了 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507213&idx=1&sn=80c320aeaf1634fb95af0e164e34c2e2&chksm=c27f9f3bf508162d003d375a737bc1c5e1289c9cfeaf37f186bedfdb5392ad74b39094fca4bb#rd) |
| 8 | 腾讯云架构师同盟专家用 Claude Code 跑通工作流后，整理成了系列专栏 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507201&idx=1&sn=e158b0e51dded9f22e762b7c616c00ff&chksm=c27f9f37f5081621bf705ec02140793bb62684336dbe8ac7bfcede5e71927db6dc819597b554#rd) |
| 9 | 开多个 Agent 后 Claude Code 账单翻了 4 倍，一个配置解决了 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507180&idx=1&sn=4ccc6b01d17918a22a4b47236807c0a1&chksm=c27f9edaf50817cc94aa01b1ab4a076c6082d0c612c1dcf4fe8af294727d5e47a2074cc140ba#rd) |
| 10 | Claude Code 接入 DeepSeek V4 实战：400 万 Tokens 从 26 降到 2 | [查看](http://mp.weixin.qq.com/s?__biz=MzkzMDI1NjcyOQ==&mid=2247507151&idx=1&sn=1ec2decd8e1372292fc8232f702cf436&chksm=c27f9ef9f50817ef385a16faa590d4a46b58e3ee4b75e25defa24d877c609c78e78883670d6a#rd) |

## 文章主题分析

从抓取到的 10 篇文章来看，该公众号主要关注以下主题:

1. **Claude Code 使用教程** - 多篇文章详细介绍 Claude Code 的使用技巧
2. **AI 编程工具** - Superpowers、cc-switch 等 AI 辅助编程工具
3. **DeepSeek 接入** - 如何在大陆地区使用 DeepSeek 等 AI 服务
4. **Agent 工作流** - AI Agent 的配置和优化
5. **实战经验** - 实际项目中的踩坑经验和最佳实践

## 技术说明

### 抓取方法

1. 使用 Python requests 库访问微信公众号合集页面
2. 解析 HTML 中的文章列表数据
3. 提取文章标题、链接等信息
4. 保存为 JSON 和 Markdown 格式

### 限制说明

- 微信公众号采用滚动加载机制，一次只能获取部分文章
- 本次只获取到最新的 10 篇文章
- 如需获取全部 32 篇文章，需要模拟滚动加载或访问更多页面

### 生成的文件

- `articles.json` - JSON 格式的文章列表
- `articles.md` - Markdown 格式的文章列表
- `wechat_album.html` - 原始 HTML 页面

## 下一步建议

如果你想要:

1. **批量改写文章内容** - 可以提供具体需求，我来帮你批量处理
2. **获取全部 32 篇文章** - 需要手动滚动页面多次，或使用浏览器自动化
3. **提取文章正文内容** - 可以遍历每篇文章链接获取详细内容
4. **定期自动抓取** - 可以设置定时任务定期抓取更新

请告诉我你的具体需求，我来帮你实现！
