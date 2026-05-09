import { defineEventHandler, handleCors, sendNoContent } from 'h3';

export default defineEventHandler((event) => {
  // 处理 OPTIONS 预检请求
  if (event.node.req.method === 'OPTIONS') {
    event.node.res.setHeader('Access-Control-Allow-Origin', '*');
    event.node.res.setHeader('Access-Control-Allow-Methods', 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS');
    event.node.res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With');
    event.node.res.statusCode = 204;
    return sendNoContent(event);
  }

  // 为所有请求添加 CORS 头
  event.node.res.setHeader('Access-Control-Allow-Origin', '*');
  event.node.res.setHeader('Access-Control-Allow-Methods', 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS');
  event.node.res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With');
});
