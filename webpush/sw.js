// Service Worker：收到推送就弹系统通知（手机通知再被手环 App 转发）
self.addEventListener("push", (e) => {
  const d = e.data ? e.data.json() : { title: "新消息", body: "" };
  e.waitUntil(self.registration.showNotification(d.title, { body: d.body }));
});
self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil(clients.openWindow("/"));
});
