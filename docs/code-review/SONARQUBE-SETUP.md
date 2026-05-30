# SonarCloud 配置指南

## 1. 注册 SonarCloud

访问 https://sonarcloud.io 并登录

## 2. 创建项目

1. 点击 "+" → "Analyze Project"
2. 选择 GitHub 仓库：kevin-lu/blog
3. 记录 Project Key 和 Organization

## 3. 配置 GitHub Secrets

在 GitHub 仓库设置中添加：
- SONAR_TOKEN: <从 SonarCloud 获取>
- SONAR_HOST_URL: https://sonarcloud.io

## 4. 验证配置

运行工作流，查看是否成功
