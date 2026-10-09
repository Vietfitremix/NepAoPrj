import axios from 'axios';
export const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || '/api', timeout: 65000, headers: { 'Content-Type': 'application/json' } });
export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) return 'Chưa thể kết nối máy chủ. Hãy kiểm tra kết nối hoặc thử lại sau.';
    if (error.response.status === 404) return 'Không tìm thấy dữ liệu này. Vui lòng bắt đầu lại từ AI Stylist.';
    if (error.response.status === 429) return 'Có nhiều yêu cầu cùng lúc. Bạn hãy thử lại sau ít giây.';
    return 'Máy chủ chưa thể xử lý yêu cầu. Vui lòng thử lại.';
  }
  return error instanceof Error ? error.message : 'Đã có lỗi xảy ra. Vui lòng thử lại.';
}
