export default defineNitroPlugin((nitroApp) => {
  nitroApp.hooks.hook('request', (event) => {
    // 为所有请求添加 CORS 头
    event.node.res.setHeader('Access-Control-Allow-Origin', '*');
    event.node.res.setHeader('Access-Control-Allow-Methods', 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS');
    event.node.res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With');
  });

  nitroApp.hooks.hook('beforeResponse', (event) => {
    // 处理 OPTIONS 预检请求
    if (event.node.req.method === 'OPTIONS') {
      event.node.res.statusCode = 204;
      event.node.res.statusMessage = 'No Content';
      return;
    }
  });
});
