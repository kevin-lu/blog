## ADDED Requirements

### Requirement: JWT Token 认证

系统应实现基于 JWT 的用户认证机制，支持 Access Token 和 Refresh Token。

#### Scenario: 用户登录
- **WHEN** 用户发送 `POST /api/v1/auth/login` 携带用户名和密码
- **THEN** 系统验证凭据，成功则返回 Access Token 和 Refresh Token

#### Scenario: 访问受保护接口
- **WHEN** 用户请求受保护的 API 接口并携带有效的 Access Token
- **THEN** 系统验证 Token 有效，返回请求的数据

#### Scenario: Token 过期
- **WHEN** 用户使用过期的 Access Token 请求受保护接口
- **THEN** 系统返回 401 Unauthorized 错误

#### Scenario: 刷新 Token
- **WHEN** 用户发送 `POST /api/v1/auth/refresh` 携带 Refresh Token
- **THEN** 系统验证 Refresh Token 有效，返回新的 Access Token

#### Scenario: 用户登出
- **WHEN** 用户发送 `POST /api/v1/auth/logout`
- **THEN** 系统使 Token 失效，清除登录状态

### Requirement: Token 安全管理

系统应实现 Token 的安全管理机制，防止 Token 被盗用。

#### Scenario: Token 黑名单
- **WHEN** 用户登出或 Token 被撤销
- **THEN** 系统将 Token 加入黑名单，在有效期内拒绝该 Token 的请求

#### Scenario: 登录失败限制
- **WHEN** 用户连续 5 次登录失败
- **THEN** 系统锁定该账户 15 分钟，防止暴力破解

#### Scenario: Token 过期时间
- **WHEN** 用户获取 Access Token
- **THEN** 系统设置 15 分钟有效期

#### Scenario: Refresh Token 过期时间
- **WHEN** 用户获取 Refresh Token
- **THEN** 系统设置 7 天有效期

### Requirement: 管理员权限验证

系统应验证管理员权限，确保只有授权用户可以访问管理接口。

#### Scenario: 管理员访问管理接口
- **WHEN** 已认证的管理员请求管理后台 API
- **THEN** 系统验证通过，返回请求数据

#### Scenario: 普通用户访问管理接口
- **WHEN** 普通用户尝试访问管理后台 API
- **THEN** 系统返回 403 Forbidden 错误

#### Scenario: 未登录用户访问管理接口
- **WHEN** 未登录用户尝试访问管理后台 API
- **THEN** 系统返回 401 Unauthorized 错误
