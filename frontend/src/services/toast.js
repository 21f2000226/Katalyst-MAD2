// toasts come up from bottom-right . calls pushToast from any view Company, admin or student
import { reactive } from "vue";

export const toastState = reactive({
  items: [],
});

let nextId = 1;

export function pushToast(text, type = "success", ttlMs = 10000) {

  if (!text) return;
  const id = nextId++;
  toastState.items.push({ id, text: String(text), type });
  window.setTimeout(() => removeToast(id), ttlMs);
  
}

export function removeToast(id) {
  const idx = toastState.items.findIndex((t) => t.id === id);
  if (idx >= 0) toastState.items.splice(idx, 1);
}
