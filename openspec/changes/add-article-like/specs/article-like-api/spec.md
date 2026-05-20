## ADDED Requirements

### Requirement: 用户可以点赞文章
系统 SHALL 允许用户对文章进行点赞操作，支持登录和未登录用户。

#### Scenario: 登录用户成功点赞
- **WHEN** 登录用户点击文章详情页的点赞按钮
- **THEN** 系统记录点赞，返回点赞成功响应，点赞数 +1

#### Scenario: 未登录用户成功点赞
- **WHEN** 未登录用户点击文章详情页的点赞按钮
- **THEN** 系统记录点赞（基于 session_id + IP），返回点赞成功响应，点赞数 +1

#### Scenario: 重复点赞被阻止
- **WHEN** 用户尝试对已点赞的文章再次点赞
- **THEN** 系统返回 409 Conflict 错误，提示"您已点赞过这篇文章"

#### Scenario: 对不存在的文章点赞
- **WHEN** 用户对不存在的文章 ID 进行点赞
- **THEN** 系统返回 404 Not Found 错误

### Requirement: 用户可以取消点赞
系统 SHALL 允许用户取消已有点赞。

#### Scenario: 成功取消点赞
- **WHEN** 用户对已点赞的文章执行取消点赞操作
- **THEN** 系统删除点赞记录，返回成功响应，点赞数 -1

#### Scenario: 取消未点赞的文章
- **WHEN** 用户对未点赞的文章执行取消点赞操作
- **THEN** 系统返回 404 或 400 错误（幂等处理）

### Requirement: 点赞操作限流防护
系统 SHALL 对点赞 API 实施 IP 限流，防止刷赞攻击。

#### Scenario: 正常频率点赞
- **WHEN** 同一 IP 在 1 分钟内点赞次数 ≤ 10 次
- **THEN** 所有点赞请求正常处理

#### Scenario: 超过限流阈值
- **WHEN** 同一 IP 在 1 分钟内点赞次数 > 10 次
- **THEN** 系统返回 429 Too Many Requests 错误，拒绝后续请求
