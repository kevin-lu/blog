---
alwaysApply: false
---
# Java Spring Cloud 微服务项目规则

> 本规则适用于大中台微服务架构，所有开发必须严格遵守

---

## 1. 技术栈约束

| 组件 | 版本 | 说明 |
|------|------|------|
| Java | 17+ | LTS 版本 |
| Spring Boot | 2.7.x | 暂不升级（历史遗留） |
| Spring Cloud | 2021.0.x | 与 Spring Boot 2.7 兼容 |
| MyBatis-Plus | 3.5.x | ORM 框架 |
| Nacos | 2.x | 注册中心 + 配置中心 |

---

## 2. 多租户实现规范

### 2.1 核心原则

```
⚠️ 最重要规则：所有数据操作必须携带 platform 字段
```

### 2.2 租户字段定义

| 字段 | 类型 | 说明 | 必须性 |
|------|------|------|--------|
| platform | String | 租户标识 | ✅ 必须 |
| tenant_id | Long | 租户 ID | 兼容旧系统 |

### 2.3 代码层实现

#### A. 实体类（Entity）

```java
// ✅ 正确示例
@Data
public class User {
    private Long id;
    private String name;
    private String platform;  // 必须字段
}

// ❌ 错误示例
@Data
public class User {
    private Long id;
    private String name;
    // 缺少 platform 字段
}
```

#### B. Service 层

```java
// ✅ 正确示例
public User getUserById(Long id) {
    String platform = TenantContext.getPlatform();
    return userMapper.selectOne(
        Wrappers.lambdaQuery(User.class)
            .eq(User::getId, id)
            .eq(User::getPlatform, platform)  // 必须携带
    );
}

// ❌ 错误示例
public User getUserById(Long id) {
    return userMapper.selectById(id);  // 没有携带 platform
}
```

#### C. Controller 层

```java
// ✅ 正确示例
@GetMapping("/{id}")
public Result<User> getUser(@PathVariable Long id) {
    // platform 从 ThreadLocal 自动获取，无需手动传参
    return Result.success(userService.getUserById(id));
}
```

---

## 3. 微服务间调用规范

### 3.1 服务调用方式

```
必须使用 Feign 远程调用
禁止使用 RestTemplate 直接调用
禁止直接查询其他服务数据库
```

### 3.2 Feign 传递租户上下文

```java
@FeignClient(name = "user-service")
public interface UserFeignClient {
    
    @GetMapping("/internal/users/{id}")
    UserDTO getUser(@PathVariable("id") Long id);
}

// 调用时自动传递 platform 头
@Configuration
public class FeignConfig implements RequestInterceptor {
    @Override
    public void apply(RequestTemplate template) {
        String platform = TenantContext.getPlatform();
        if (StrUtil.isNotBlank(platform)) {
            template.header("X-Platform", platform);
        }
    }
}
```

### 3.3 被调用服务接收租户上下文

```java
@RestController
@RequestMapping("/internal")
public class InternalController {
    
    @GetMapping("/users/{id}")
    public UserDTO getUser(@PathVariable Long id,
                          @RequestHeader(value = "X-Platform", required = false) String platform) {
        // 设置到 ThreadLocal
        if (StrUtil.isNotBlank(platform)) {
            TenantContext.setPlatform(platform);
        }
        return userService.getUserById(id);
    }
}
```

---

## 4. 数据库设计规范

### 4.1 表结构要求

```sql
-- ✅ 正确：所有租户表必须包含 platform 字段
CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL COMMENT '租户标识',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_platform (platform),
    INDEX idx_platform_username (platform, username)
);

-- ❌ 错误：缺少 platform 字段
CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 MyBatis-Plus 多租户插件

```java
@Configuration
public class MyBatisPlusConfig {
    
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        
        // 多租户插件
        interceptor.addInnerInterceptor(new TenantLineInnerInterceptor(new TenantLineHandler() {
            @Override
            public Expression getTenantId() {
                // 从 ThreadLocal 获取当前租户
                return new StringFunction("'" + TenantContext.getPlatform() + "'");
            }
            
            @Override
            public String getTenantIdColumn() {
                return "platform";
            }
            
            @Override
            public boolean ignoreTable(String tableName) {
                // 系统表不需要租户隔离
                return Arrays.asList("sys_dict", "sys_config").contains(tableName);
            }
        }));
        
        return interceptor;
    }
}
```

---

## 5. 异常处理规范

### 5.1 租户未设置异常

```java
// 抛出租户上下文缺失异常
if (TenantContext.getPlatform() == null) {
    throw new BizException("租户上下文未设置，请检查请求头 X-Platform");
}
```

### 5.2 全局异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BizException.class)
    public Result<?> handleBizException(BizException e) {
        return Result.error(e.getCode(), e.getMessage());
    }
}
```

---

## 6. API 设计规范

### 6.1 接口路径

```
/{module}/{entity}/{action}

/示例：
POST   /user/user/create      - 创建用户
GET    /user/user/{id}        - 获取用户
PUT    /user/user/update      - 更新用户
DELETE /user/user/{id}        - 删除用户
GET    /user/user/list        - 查询用户列表
```

### 6.2 响应格式

```java
// ✅ 统一响应格式
public class Result<T> {
    private Integer code;
    private String message;
    private T data;
    
    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.setCode(200);
        result.setMessage("success");
        result.setData(data);
        return result;
    }
}
```

---

## 7. 配置管理

### 7.1 Nacos 配置

```
# application.yml
spring:
  application:
    name: {service-name}
  cloud:
    nacos:
      discovery:
        server-addr: ${NACOS_HOST:127.0.0.1:8848}
      config:
        server-addr: ${NACOS_HOST:127.0.0.1:8848}
        file-extension: yml
```

### 7.2 环境隔离

```
dev.yaml    - 开发环境
test.yaml   - 测试环境
prod.yaml   - 生产环境
```

---

## 8. 代码审查清单

开发完成后自检：

- [ ] **platform 字段**：所有实体类是否包含 `platform` 字段
- [ ] **查询条件**：所有查询 SQL 是否携带 `platform` 条件
- [ ] **新增操作**：新增数据是否自动设置 `platform`
- [ ] **服务调用**：跨服务调用是否传递 `X-Platform` 头
- [ ] **ThreadLocal**：请求入口是否正确设置 `TenantContext`
- [ ] **异常处理**：缺少租户上下文时是否有明确提示

---

## 9. 常见错误示例

### ❌ 错误 1：跨租户数据泄露

```java
// 错误：没有携带 platform 查询
public List<User> listAll() {
    return userMapper.selectList(null);  // 会查出所有租户数据！
}

// 正确：携带 platform
public List<User> listAll() {
    String platform = TenantContext.getPlatform();
    return userMapper.selectList(
        Wrappers.lambdaQuery(User.class)
            .eq(User::getPlatform, platform)
    );
}
```

### ❌ 错误 2：新增时遗漏 platform

```java
// 错误：新增用户时没有设置 platform
public void createUser(User user) {
    userMapper.insert(user);  // platform 为空！
}

// 正确：自动设置 platform
public void createUser(User user) {
    user.setPlatform(TenantContext.getPlatform());
    userMapper.insert(user);
}
```

### ❌ 错误 3：硬编码 platform

```java
// 错误：硬编码租户
public User getUserById(Long id) {
    return userMapper.selectOne(
        Wrappers.lambdaQuery(User.class)
            .eq(User::getPlatform, "platform_a")  // 硬编码！
    );
}

// 正确：从上下文获取
public User getUserById(Long id) {
    String platform = TenantContext.getPlatform();
    return userMapper.selectOne(
        Wrappers.lambdaQuery(User.class)
            .eq(User::getPlatform, platform)
    );
}
```

---

## 10. 相关文件

| 文件 | 说明 |
|------|------|
| `TenantContext.java` | 租户上下文 ThreadLocal 工具类 |
| `TenantInterceptor.java` | HTTP 请求租户拦截器 |
| `TenantLineHandler.java` | MyBatis-Plus 多租户处理器 |

---

**⚠️ 警告**：违反以上规则可能导致：
1. 数据泄露（跨租户访问）
2. 数据污染（数据串租户）
3. 系统安全问题
