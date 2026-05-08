import { useMessage, useNotification } from 'naive-ui';

export function useNotification() {
  const message = useMessage();
  const notification = useNotification();

  const success = (content: string) => {
    message.success(content);
  };

  const error = (content: string) => {
    message.error(content);
  };

  const warning = (content: string) => {
    message.warning(content);
  };

  const info = (content: string) => {
    message.info(content);
  };

  const notifySuccess = (title: string, content?: string) => {
    notification.success({
      title,
      content,
      duration: 3000,
    });
  };

  const notifyError = (title: string, content?: string) => {
    notification.error({
      title,
      content,
      duration: 3000,
    });
  };

  const notifyWarning = (title: string, content?: string) => {
    notification.warning({
      title,
      content,
      duration: 3000,
    });
  };

  const notifyInfo = (title: string, content?: string) => {
    notification.info({
      title,
      content,
      duration: 3000,
    });
  };

  return {
    success,
    error,
    warning,
    info,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
  };
}
