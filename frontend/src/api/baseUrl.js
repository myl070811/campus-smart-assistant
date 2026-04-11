/**
 * 后端 API 根地址：
 * - 默认空字符串：走同源 `/api`（Docker + nginx 推荐）
 * - 本地前后端分离可通过 VITE_API_BASE_URL 指向后端 origin（如 http://127.0.0.1:5000）
 */
const raw = String(import.meta.env.VITE_API_BASE_URL ?? '').trim()
const cleaned = raw.replace(/\/+$/, '')

// 防止误配为 "/api" 导致后续拼接成 "/api/api/*"
export const API_BASE = cleaned === '/' || cleaned === '/api' ? '' : cleaned
