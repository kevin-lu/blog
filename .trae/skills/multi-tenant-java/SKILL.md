# Multi-Tenant Java 开发技能

> 适用于 Spring Cloud 微服务多租户 SaaS 平台开发

## 技能定义

**技能名称**：multi-tenant-java  
**触发条件**：
- 开发 Java Spring Cloud 微服务
- 需要实现多租户隔离
- 需要在项目中添加租户相关功能

**前置要求**：
- 熟悉 Java 17+
- 熟悉 Spring Boot / Spring Cloud
- 熟悉 MyBatis-Plus

---

## 核心流程

### 1️⃣ 理解租户方案

**本技能采用字段隔离方案**：
- 使用 `platform` 字段作为租户标识
- 所有数据操作必须携带 `platform` 条件
- 通过 ThreadLocal 实现租户上下文传递

### 2️⃣ 项目检查清单

开始开发前检查：

```
□ 项目是否配置了 TenantContext.java
□ 是否配置了 TenantInterceptor.java
□ 是否配置了 MyBatis-Plus 多租户插件
□ 实体类是否包含 platform 字段
□ 代码模板是否符合规范
```

### 3️⃣ 开发流程

#### Step 1: 检查租户基础设施

```bash
# 检查是否存在租户上下文工具类
ls -la src/main/java/**/TenantContext.java

# 检查是否存在租户拦截器
ls -la src/main/java/**/TenantInterceptor.java

# 检查 MyBatis-Plus 配置
cat src/main/resources/application.yml | grep -A5 tenant
```

#### Step 2: 创建租户上下文（如果不存在）

```java
@Component
public class TenantContext {
    
    private static final ThreadLocal<String> TENANT = new ThreadLocal<>();
    
    public static String getPlatform() {
        return TENANT.get();
    }
    
    public static void setPlatform(String platform) {
        TENANT.set(platform);
    }
    
    public static void clear() {
        TENANT.remove();
    }
}
```

#### Step 3: 创建租户拦截器

```java
@Component
public class TenantInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, 
                            Object handler) {
        String platform = request.getHeader("X-Platform");
        if (StrUtil.isNotBlank(platform)) {
            TenantContext.setPlatform(platform);
        }
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                               HttpServletResponse response, 
                               Object handler, Exception ex) {
        TenantContext.clear();
    }
}
```

#### Step 4: 配置拦截器

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    
    @Autowired
    private TenantInterceptor tenantInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(tenantInterceptor)
                .addPathPatterns("/**")
                .excludePathPatterns("/health", "/actuator/**");
    }
}
```

#### Step 5: 配置 MyBatis-Plus 多租户插件

```java
@Configuration
public class MyBatisPlusConfig {
    
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new TenantLineInnerInterceptor(new TenantLineHandler() {
            
            @Override
            public Expression getTenantId() {
                String platform = TenantContext.getPlatform();
                if (StrUtil.isBlank(platform)) {
                    throw new BizException("租户上下文未设置");
                }
                return new StringFunction("'" + platform + "'");
            }
            
            @Override
            public String getTenantIdColumn() {
                return "platform";
            }
            
            @Override
            public boolean ignoreTable(String tableName) {
                // 系统表不需要租户隔离
                return Arrays.asList(
                    "sys_dict", 
                    "sys_config",
                    "sys_menu"
                ).contains(tableName);
            }
        }));
        
        return interceptor;
    }
}
```

### 4️⃣ 新增功能模板

#### Entity 模板

```java
@Data
public class XxxEntity {
    
    private Long id;
    
    private String name;
    
    private String platform;  // ⚠️ 必须字段
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
}
```

#### Service 模板

```java
@Service
public class XxxServiceImpl implements XxxService {
    
    @Autowired
    private XxxMapper xxxMapper;
    
    @Override
    public XxxDTO getById(Long id) {
        // platform 从 ThreadLocal 自动获取
        XxxEntity entity = xxxMapper.selectById(id);
        return BeanCopyUtil.copy(entity, XxxDTO.class);
    }
    
    @Override
    public void create(XxxDTO dto) {
        XxxEntity entity = BeanCopyUtil.copy(dto, XxxEntity.class);
        entity.setPlatform(TenantContext.getPlatform());  // 自动设置
        xxxMapper.insert(entity);
    }
    
    @Override
    public PageResult<XxxDTO> page(XxxQuery query) {
        Page<XxxEntity> page = xxxMapper.selectPage(
            Page.of(query.getPageNum(), query.getPageSize()),
            Wrappers.lambdaQuery(XxxEntity.class)
                .like(StrUtil.isNotBlank(query.getName()), 
                      XxxEntity::getName, query.getName())
                .orderByDesc(XxxEntity::getCreatedAt)
        );
        
        return PageResult.of(
            page.getRecords().stream()
                .map(e -> BeanCopyUtil.copy(e, XxxDTO.class))
                .collect(Collectors.toList()),
            page.getTotal()
        );
    }
}
```

#### Controller 模板

```java
@RestController
@RequestMapping("/xxx")
public class XxxController {
    
    @Autowired
    private XxxService xxxService;
    
    @PostMapping("/create")
    public Result<Void> create(@RequestBody XxxDTO dto) {
        xxxService.create(dto);
        return Result.success();
    }
    
    @GetMapping("/{id}")
    public Result<XxxDTO> getById(@PathVariable Long id) {
        return Result.success(xxxService.getById(id));
    }
    
    @GetMapping("/page")
    public Result<PageResult<XxxDTO>> page(XxxQuery query) {
        return Result.success(xxxService.page(query));
    }
}
```

### 5️⃣ 常见问题处理

#### Q1: 如何处理跨服务查询？

```java
// 调用方
@FeignClient(name = "target-service")
public interface TargetFeignClient {
    
    @GetMapping("/internal/xxx/{id}")
    XxxDTO getById(@PathVariable Long id);
}

// 被调用方 Controller
@RestController
@RequestMapping("/internal")
public class InternalController {
    
    @GetMapping("/xxx/{id}")
    public XxxDTO getById(@PathVariable Long id,
                          @RequestHeader(value = "X-Platform", required = false) String platform) {
        if (StrUtil.isNotBlank(platform)) {
            TenantContext.setPlatform(platform);
        }
        return xxxService.getById(id);
    }
}
```

#### Q2: 如何处理批量导入？

```java
@Override
public void importBatch(List<XxxDTO> dtoList) {
    String platform = TenantContext.getPlatform();
    
    List<XxxEntity> entities = dtoList.stream()
        .map(dto -> {
            XxxEntity entity = BeanCopyUtil.copy(dto, XxxEntity.class);
            entity.setPlatform(platform);  // 批量设置
            return entity;
        })
        .collect(Collectors.toList());
    
    xxxService.saveBatch(entities);
}
```

#### Q3: 如何处理数据权限？

```java
// 复杂数据权限场景，手动添加条件
public List<XxxDTO> listByConditions(XxxQuery query) {
    return xxxMapper.selectList(
        Wrappers.lambdaQuery(XxxEntity.class)
            .eq(XxxEntity::getPlatform, TenantContext.getPlatform())
            .eq(query.getStatus() != null, 
                XxxEntity::getStatus, query.getStatus())
            .ge(query.getStartDate() != null, 
                XxxEntity::getCreatedAt, query.getStartDate())
            .le(query.getEndDate() != null, 
                XxxEntity::getCreatedAt, query.getEndDate())
    ).stream()
      .map(e -> BeanCopyUtil.copy(e, XxxDTO.class))
      .collect(Collectors.toList());
}
```

---

## 代码审查标准

| 检查项 | 权重 | 说明 |
|-------|------|------|
| platform 字段存在 | ⭐⭐⭐ | 所有实体类必须包含 |
| 新增设置 platform | ⭐⭐⭐ | 使用 TenantContext.getPlatform() |
| 查询携带 platform | ⭐⭐⭐ | 避免数据泄露 |
| 服务调用传递头 | ⭐⭐ | Feign 调用需传递 X-Platform |
| 异常处理 | ⭐⭐ | 租户为空时明确提示 |

---

## 相关资源

- **项目规则**：`.trae/rules/project_rules.md`
- **示例代码**：`src/main/java/com/example/demo/tenant/`
- **测试用例**：`src/test/java/**/tenant/`
