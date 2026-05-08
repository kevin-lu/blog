export const adminConfig = {
  name: '博客管理后台',
  version: '1.0.0',
  apiPrefix: '/api/admin',
  jwt: {
    expiresIn: '7d',
  },
  pagination: {
    defaultPageSize: 20,
    pageSizes: [10, 20, 50, 100],
  },
};
