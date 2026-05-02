# 多租户开发快速参考

## 核心命令

### 检查租户配置
```bash
# 检查租户上下文
find . -name "TenantContext.java"

# 检查拦截器
find . -name "TenantInterceptor.java"

# 检查多租户插件
grep -r "TenantLineInnerInterceptor" .
```

### 验证代码
```bash
# 检查实体类是否包含 platform
grep -l "platform" src/main/java/**/entity/*.java

# 检查新增操作是否设置 platform
grep -A5 "insert\|save" src/main/java/**/service/*.java
```

---

## 常用代码片段

### 获取当前租户
```java
String platform = TenantContext.getPlatform();
```

### 设置租户（新增时）
```java
entity.setPlatform(TenantContext.getPlatform());
```

### 查询条件（手动）
```java
Wrappers.lambdaQuery(Entity.class)
    .eq(Entity::getPlatform, TenantContext.getPlatform())
```

---

## 常见错误

| 错误 | 后果 | 修复 |
|------|------|------|
| 新增没有设置 platform | 数据无租户 | `entity.setPlatform(...)` |
| 查询没有带 platform | 数据泄露 | 添加 `.eq(Entity::getPlatform, ...)` |
| 硬编码租户 | 只支持单租户 | 改用 `TenantContext.getPlatform()` |

---

## 测试验证

```java
@Test
public void testMultiTenant() {
    // 设置租户 A
    TenantContext.setPlatform("platform_a");
    service.create(dtoA);
    
    // 切换到租户 B
    TenantContext.setPlatform("platform_b");
    service.create(dtoB);
    
    // 验证：租户 A 看不到租户 B 的数据
    TenantContext.setPlatform("platform_a");
    List<DTO> list = service.list();
    assertTrue(list.stream().noneMatch(d -> d.getName().equals("B")));
}
```
