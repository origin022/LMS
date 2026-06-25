export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://lms-backend-t7q6.onrender.com/api/v1';
export const FILE_URL = (import.meta.env.VITE_API_URL || 'https://lms-backend-t7q6.onrender.com/').replace(/\/$/, '') + '/';

// Logic to derive WS_URL from BASE_URL
export const WS_URL = BASE_URL.replace(/^http/, 'ws');


export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const token = localStorage.getItem("token");


    const headers: Record<string, string> = {
        'Accept': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...((options.headers as Record<string, string>) || {})
    };

    if (!headers['Content-Type']) {
        if (options.body instanceof FormData) {
        } else if (options.body instanceof URLSearchParams) {
            headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8';
        } else if (options.body) {
            headers['Content-Type'] = 'application/json';
        }
    }

    return fetch(`${BASE_URL}/${endpoint.replace(/^\//, '')}`, {
        ...options,
        credentials: 'include',
        headers
        //defaultOptions
    });
}

export function extractErrorMessage(detail: any): string {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail.map(d => {
          if (typeof d === 'string') return d;
          const msg = d.msg || '';
          const loc = d.loc ? d.loc[d.loc.length - 1] : '';
          
          let translatedMsg = msg;
          if (msg === 'field required') translatedMsg = 'حقل مطلوب';
          else if (msg.includes('value is not a valid email')) translatedMsg = 'البريد الإلكتروني غير صالح';
          else if (msg.includes('ensure this value has at least')) translatedMsg = 'القيمة قصيرة جداً';
          
          let translatedField = loc;
          if (loc === 'name') translatedField = 'الاسم';
          else if (loc === 'email') translatedField = 'البريد الإلكتروني';
          else if (loc === 'password') translatedField = 'كلمة المرور';
          else if (loc === 'phone') translatedField = 'رقم الهاتف';
          else if (loc === 'roles_id') translatedField = 'نوع الحساب';
          else if (loc === 'department_id') translatedField = 'القسم';

          return translatedField ? `${translatedField}: ${translatedMsg}` : translatedMsg;
        }).join(' | ');
    }
    if (typeof detail === 'object' && detail !== null) {
        return JSON.stringify(detail);
    }
    return "حدث خطأ غير معروف";
}
 